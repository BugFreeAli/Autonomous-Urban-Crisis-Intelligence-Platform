import logging
import uuid
from typing import List
from .base import BaseAgent
from . import narrative as narr
from ..orchestration.events import (
    BaseEvent,
    SocialSignalEvent,
    WeatherUpdateEvent,
    TrafficUpdateEvent,
    FieldReportEvent,
    HospitalLoadIncreased,
    ResourceDispatched,
    IncidentHypothesisEvent,
    CredibilityVerifiedEvent,
    ContradictionDetectedEvent,
    CrisisClassifiedEvent,
    CascadePredictedEvent,
    EventPriority,
    IncidentRetractedEvent,
    HumanVerificationEscalationEvent,
    IncidentMergedEvent,
)
from ..state.models import Incident, IncidentStatus, Resource
from .cascade_engine import CascadePredictionEngine
from ..optimization.engine import ResourceOptimizationEngine
from ..verification.engine import VerificationEngine
from ..communication.engine import StakeholderMessagingEngine

logger = logging.getLogger(__name__)


class SignalIntelligenceAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, agent_name="SignalIntelligenceAgent", **kwargs)
        self.subscribe(SocialSignalEvent)
        self.subscribe(WeatherUpdateEvent)
        self.subscribe(TrafficUpdateEvent)
        self.subscribe(FieldReportEvent)
        self._signal_buffer: List[BaseEvent] = []

    async def process_event(self, event: BaseEvent) -> None:
        self._signal_buffer.append(event)
        if len(self._signal_buffer) > 50:
            self._signal_buffer.pop(0)

        loc = event.payload.get("location") or event.payload.get("district")
        if not loc:
            return

        cluster = [
            s
            for s in self._signal_buffer
            if (s.payload.get("location") == loc or s.payload.get("district") == loc)
        ]

        if len(cluster) < 3:
            return

        types = set(type(s).__name__ for s in cluster)
        if "WeatherUpdateEvent" in types and "SocialSignalEvent" in types:
            suspected_type = "Severe Weather / Flooding"
        elif "TrafficUpdateEvent" in types:
            suspected_type = "Traffic Collapse"
        else:
            suspected_type = "Unknown Anomaly"

        if self.intelligence_engine:
            reasoning = await self.intelligence_engine.reason(
                f"In plain language, explain why {len(cluster)} signals in {narr.sector(loc)} suggest {suspected_type}. "
                f"One short paragraph, no jargon.",
                context=f"Signal types: {types}",
            )
        else:
            reasoning = narr.signal_cluster_summary(loc, suspected_type, len(cluster))

        hyp_evt = IncidentHypothesisEvent(
            event_id=f"hyp-{uuid.uuid4().hex[:6]}",
            source=self.agent_name,
            priority=EventPriority.HIGH,
            payload={
                "location": loc,
                "signal_count": len(cluster),
                "suspected_type": suspected_type,
                "signals": [s.event_id for s in cluster],
                "raw_credibilities": [
                    s.payload.get("credibility", 0.5)
                    for s in cluster
                    if isinstance(s, SocialSignalEvent)
                ],
            },
        )
        await self.emit_decision(hyp_evt)
        self._signal_buffer = [s for s in self._signal_buffer if s not in cluster]

        self.log_reasoning(
            "AssessSignals",
            reasoning,
            0.6,
            event.event_id,
        )
        self.log_outcome(
            f"Flagged possible {suspected_type} in {narr.sector(loc)}",
            f"I grouped {len(cluster)} reports and sent them for verification. "
            f"No units or public alerts yet — waiting for credibility checks.",
            0.6,
            event.event_id,
            outcome_type="detect",
        )


class CredibilityAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, agent_name="CredibilityAgent", **kwargs)
        self.subscribe(IncidentHypothesisEvent)
        self.engine = VerificationEngine()

    async def process_event(self, event: BaseEvent) -> None:
        if not isinstance(event, IncidentHypothesisEvent):
            return

        state = await self.state_manager.get_state()
        result = self.engine.evaluate_hypothesis(event.payload, state)
        loc = event.payload.get("location", "Unknown")
        ctype = event.payload.get("suspected_type", "Unknown")

        self.log_reasoning(
            "VerifyReport",
            narr.verification_thinking(
                result.reasoning_trace, result.action, result.final_confidence, loc, ctype
            ),
            result.final_confidence,
            event.event_id,
        )

        headline = narr.verification_outcome_headline(result.action, loc, ctype)
        body = narr.verification_outcome_body(result.action, result.final_confidence, loc, ctype)

        if result.action == "RETRACT":
            await self.emit_decision(
                IncidentRetractedEvent(
                    event_id=f"ret-{uuid.uuid4()}",
                    source=self.agent_name,
                    payload={
                        "incident_id": result.incident_id,
                        "reason": "Low credibility / misinformation",
                        "location": loc,
                    },
                )
            )
            self.log_outcome(headline, body, result.final_confidence, event.event_id, outcome_type="retract")

        elif result.action == "ESCALATE_HUMAN":
            await self.emit_decision(
                HumanVerificationEscalationEvent(
                    event_id=f"hve-{uuid.uuid4()}",
                    source=self.agent_name,
                    priority=EventPriority.CRITICAL,
                    payload={
                        "incident_id": result.incident_id,
                        "reason": "Conflicting signals",
                        "location": loc,
                    },
                )
            )
            self.log_outcome(headline, body, result.final_confidence, event.event_id, outcome_type="escalate")

        elif result.action == "MERGE":
            await self.emit_decision(
                IncidentMergedEvent(
                    event_id=f"mrg-{uuid.uuid4()}",
                    source=self.agent_name,
                    payload={
                        "source_incident": result.incident_id,
                        "target_incident": result.merge_target,
                        "location": loc,
                    },
                )
            )
            self.log_outcome(
                headline,
                body,
                result.final_confidence,
                event.event_id,
                impacts=[f"Duplicate folded into incident {result.merge_target}"],
                outcome_type="merge",
            )

        else:
            await self.emit_decision(
                CredibilityVerifiedEvent(
                    event_id=f"ver-{uuid.uuid4()}",
                    source=self.agent_name,
                    priority=EventPriority.HIGH,
                    payload={
                        "incident_id": result.incident_id,
                        "location": loc,
                        "suspected_type": ctype,
                        "derived_confidence": result.final_confidence,
                        "signal_count": event.payload.get("signal_count", 1),
                    },
                )
            )
            self.log_outcome(headline, body, result.final_confidence, event.event_id, outcome_type="confirm")


class CrisisClassificationAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, agent_name="CrisisClassificationAgent", **kwargs)
        self.subscribe(CredibilityVerifiedEvent)
        self.subscribe(ContradictionDetectedEvent)
        self.subscribe(IncidentRetractedEvent)
        self.subscribe(IncidentMergedEvent)
        self.subscribe(HumanVerificationEscalationEvent)

    async def _bump_crisis_level(self, confidence: float) -> None:
        state = await self.state_manager.get_state()
        new_level = max(state.crisis_confidence, confidence)
        await self.state_manager.update_crisis_confidence(new_level)

    async def process_event(self, event: BaseEvent) -> None:
        state = await self.state_manager.get_state()

        if isinstance(event, IncidentRetractedEvent):
            inc_id = event.payload.get("incident_id")
            loc = event.payload.get("location", "")
            if inc_id in state.active_incidents:
                inc = state.active_incidents[inc_id]
                inc.status = IncidentStatus.RETRACTED
                inc.confidence_score = 0.0
                await self.state_manager.update_incident(inc)
            self.log_outcome(
                f"Closed false alarm in {narr.sector(loc) if loc else 'city'}",
                "The incident is marked retracted in the city map. Public correction messages will follow.",
                1.0,
                event.event_id,
                outcome_type="retract",
            )
            return

        if isinstance(event, IncidentMergedEvent):
            src_id = event.payload.get("source_incident")
            tgt_id = event.payload.get("target_incident")
            if tgt_id in state.active_incidents and src_id in state.active_incidents:
                src_inc = state.active_incidents[src_id]
                tgt_inc = state.active_incidents[tgt_id]
                tgt_inc.signals_clustered += src_inc.signals_clustered
                tgt_inc.confidence_score = min(1.0, tgt_inc.confidence_score + 0.1)
                src_inc.status = IncidentStatus.RETRACTED
                await self.state_manager.update_incident(src_inc)
                await self.state_manager.update_incident(tgt_inc)
            merge_conf = (
                state.active_incidents[tgt_id].confidence_score
                if tgt_id in state.active_incidents
                else 0.8
            )
            self.log_outcome(
                "Combined duplicate incident reports",
                f"All activity now tracked under incident {tgt_id}. Operators see one crisis, not two.",
                merge_conf,
                event.event_id,
                outcome_type="merge",
            )
            return

        if isinstance(event, HumanVerificationEscalationEvent):
            self.log_outcome(
                "Autonomous response paused",
                "No further automatic dispatches until a human operator clears this conflict.",
                1.0,
                event.event_id,
                outcome_type="escalate",
            )
            return

        if isinstance(event, ContradictionDetectedEvent):
            loc = event.payload.get("location", "")
            state = await self.state_manager.get_state()
            for inc in state.active_incidents.values():
                if inc.location == loc and inc.status in [
                    IncidentStatus.EMERGING,
                    IncidentStatus.SUSPECTED,
                ]:
                    inc.contradiction_flag = True
                    inc.confidence_score *= 0.5
                    await self.state_manager.update_incident(inc)
            self.log_reasoning(
                "ContradictionFlag",
                f"Conflicting reports in {narr.sector(loc)}. I lowered confidence on open incidents until verification finishes.",
                0.4,
                event.event_id,
            )
            return

        if isinstance(event, CredibilityVerifiedEvent):
            loc = event.payload["location"]
            conf = event.payload["derived_confidence"]
            ctype = event.payload["suspected_type"]
            count = event.payload["signal_count"]
            where = narr.sector(loc)

            state = await self.state_manager.get_state()
            existing = [
                i
                for i in state.active_incidents.values()
                if i.location == loc and i.status != IncidentStatus.RESOLVED
            ]

            if existing:
                inc = existing[0]
                inc.confidence_score = conf
                inc.signals_clustered += count
                if conf > 0.8:
                    inc.status = IncidentStatus.CONFIRMED
                elif conf > 0.5:
                    inc.status = IncidentStatus.PROBABLE
                await self.state_manager.update_incident(inc)
                await self._bump_crisis_level(conf)
                await self.emit_decision(
                    CrisisClassifiedEvent(
                        event_id=f"cls-{uuid.uuid4()}",
                        source=self.agent_name,
                        payload={"incident": inc.model_dump()},
                    )
                )
                self.log_outcome(
                    f"Upgraded {ctype} in {where} to {inc.status.value}",
                    f"Official incident {inc.incident_id} is now at {narr.pct(inc.severity)} severity. "
                    f"Cascade and resource agents are activated.",
                    conf,
                    event.event_id,
                    impacts=[f"Incident ID: {inc.incident_id}", f"Status: {inc.status.value}"],
                    outcome_type="classify",
                )
            else:
                new_inc = Incident(
                    incident_id=f"inc-{uuid.uuid4()}",
                    type=ctype,
                    severity=0.3 + (conf * 0.3),
                    location=loc,
                    reported_at=event.timestamp,
                    status=IncidentStatus.SUSPECTED if conf < 0.7 else IncidentStatus.PROBABLE,
                    confidence_score=conf,
                    signals_clustered=count,
                    prediction_tags=["Traffic Disruption", "Hospital Loading"],
                )
                await self.state_manager.update_incident(new_inc)
                await self._bump_crisis_level(conf)
                await self.emit_decision(
                    CrisisClassifiedEvent(
                        event_id=f"cls-{uuid.uuid4()}",
                        source=self.agent_name,
                        payload={"incident": new_inc.model_dump()},
                    )
                )
                self.log_outcome(
                    f"Opened official incident: {ctype} in {where}",
                    f"Incident {new_inc.incident_id} is live on the command map at {new_inc.status.value} status. "
                    f"Downstream agents will plan cascades, dispatch units, and draft alerts.",
                    conf,
                    event.event_id,
                    impacts=[
                        f"Severity estimate: {narr.pct(new_inc.severity)}",
                        f"Tracking {count} corroborating signals",
                    ],
                    outcome_type="classify",
                )


class CascadePredictionAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, agent_name="CascadePredictionAgent", **kwargs)
        self.subscribe(CrisisClassifiedEvent)
        self.engine = CascadePredictionEngine()

    async def process_event(self, event: BaseEvent) -> None:
        if not isinstance(event, CrisisClassifiedEvent):
            return

        state = await self.state_manager.get_state()
        predictions = self.engine.predict_cascades(state, event.timestamp)
        if not predictions:
            return

        impacts = []
        for p in predictions[:4]:
            mins = int((p.estimated_time - event.timestamp).total_seconds() / 60)
            impacts.append(
                f"In ~{mins} min: {p.consequence_type} near {narr.sector(p.target_entity_id)} "
                f"({narr.pct(p.probability)} likely)"
            )

        await self.emit_decision(
            CascadePredictedEvent(
                event_id=f"casc-{uuid.uuid4()}",
                source=self.agent_name,
                payload={"predictions": [p.model_dump() for p in predictions]},
            )
        )

        top = predictions[0]
        self.log_reasoning(
            "ForecastCascades",
            "I modeled second- and third-order effects if we do nothing (traffic, hospitals, power).",
            top.severity_impact,
            event.event_id,
            trade_offs=impacts,
        )
        self.log_outcome(
            f"Warning: {top.consequence_type} likely next",
            f"If we do not intervene, the city should expect {top.consequence_type} "
            f"around {narr.sector(top.target_entity_id)}. Hospitals and traffic teams are being advised.",
            top.probability,
            event.event_id,
            impacts=impacts,
            outcome_type="forecast",
        )


class ResourceOptimizationAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, agent_name="ResourceOptimizationAgent", **kwargs)
        self.subscribe(CrisisClassifiedEvent)
        self.subscribe(CascadePredictedEvent)
        self.subscribe(HospitalLoadIncreased)
        self.engine = ResourceOptimizationEngine()

    async def process_event(self, event: BaseEvent) -> None:
        state = await self.state_manager.get_state()
        actions, confidence, reasoning = self.engine.optimize_allocation(state)

        if not actions:
            self.log_reasoning(
                "ResourceStandby",
                "No active crises need emergency units right now. All available assets stay in reserve.",
                0.9,
                event.event_id,
            )
            return

        dispatch_lines = []
        for act in actions:
            res = state.resources.get(act.resource_id)
            if res:
                res.status = "Dispatched"
                res.target_location = act.target_location
                res.location = res.location or act.target_location
                res.eta_seconds = act.estimated_eta
                await self.state_manager.update_resource(res)

            await self.emit_decision(
                ResourceDispatched(
                    event_id=f"disp-{uuid.uuid4().hex[:8]}",
                    source=self.agent_name,
                    priority=EventPriority.HIGH,
                    payload={
                        "resource_id": act.resource_id,
                        "target_location": act.target_location,
                        "eta_seconds": act.estimated_eta,
                        "type": res.type if res else "Unit",
                    },
                )
            )
            unit = res.type if res else "Unit"
            where = narr.sector(act.target_location)
            dispatch_lines.append(
                f"{unit} {act.resource_id} → {where} (ETA {act.estimated_eta}s)"
            )

        self.log_reasoning(
            "PlanDispatch",
            "I matched open incidents to the nearest available ambulances and fire crews.\n"
            + "\n".join(f"  • {r}" for r in reasoning),
            confidence,
            event.event_id,
        )
        self.log_outcome(
            f"Dispatched {len(actions)} emergency unit{'s' if len(actions) != 1 else ''}",
            "Units are rolling to contain active incidents and slow cascade damage.",
            confidence,
            event.event_id,
            impacts=dispatch_lines,
            outcome_type="dispatch",
        )


class SimulationAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, agent_name="SimulationAgent", **kwargs)

    async def process_event(self, event: BaseEvent) -> None:
        pass


class RecoveryAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, agent_name="RecoveryAgent", **kwargs)
        self.subscribe(ResourceDispatched)

    async def process_event(self, event: BaseEvent) -> None:
        payload = event.payload
        rid = payload.get("resource_id", "unit")
        where = narr.sector(payload.get("target_location", ""))
        eta = payload.get("eta_seconds", 0)
        self.log_reasoning(
            "TrackMitigation",
            f"I am watching {rid} en route to {where}. I will measure whether severity drops once the unit is on scene.",
            0.9,
            event.event_id,
        )


class StakeholderCommunicationAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, agent_name="StakeholderCommunicationAgent", **kwargs)
        self.subscribe(CrisisClassifiedEvent)
        self.subscribe(CascadePredictedEvent)
        self.subscribe(IncidentRetractedEvent)
        self.subscribe(ResourceDispatched)
        self.engine = StakeholderMessagingEngine()

    async def process_event(self, event: BaseEvent) -> None:
        state = await self.state_manager.get_state()
        messages = []

        if isinstance(event, IncidentRetractedEvent):
            messages = self.engine.generate_briefs("IncidentRetracted", state, event.payload)
        elif isinstance(event, CascadePredictedEvent):
            messages = self.engine.generate_briefs("CascadePredicted", state, event.payload)
        elif isinstance(event, CrisisClassifiedEvent):
            messages = self.engine.generate_briefs("CrisisClassified", state, event.payload)
        elif isinstance(event, ResourceDispatched):
            messages = self.engine.generate_briefs("ResourceDispatched", state, event.payload)

        for msg in messages:
            logger.info(f"[{msg.priority}] TO {msg.stakeholder} ({msg.channel}): {msg.message}")
            self.log_outcome(
                f"{msg.stakeholder} alert via {msg.channel}",
                msg.message,
                0.95 if msg.priority in ("Critical", "High") else 0.75,
                event.event_id,
                impacts=[f"Priority: {msg.priority}"],
                outcome_type="comms",
            )


class CentralCommandAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, agent_name="CentralCommandAgent", **kwargs)
        self.subscribe(ResourceDispatched)
        self.subscribe(CrisisClassifiedEvent)

    async def process_event(self, event: BaseEvent) -> None:
        if isinstance(event, ResourceDispatched):
            payload = event.payload
            rid = payload.get("resource_id")
            where = narr.sector(payload.get("target_location", ""))
            eta = payload.get("eta_seconds", 0)
            unit = payload.get("type", "Unit")

            state = await self.state_manager.get_state()
            if rid and rid in state.resources:
                res = state.resources[rid]
                res.status = "Dispatched"
                res.target_location = payload.get("target_location")
                res.eta_seconds = eta
                await self.state_manager.update_resource(res)

            self.log_outcome(
                f"Command confirmed: {unit} {rid} deployed",
                f"Central command logged the dispatch to {where}. "
                f"Operators should see the unit on the map with ~{eta}s ETA.",
                1.0,
                event.event_id,
                impacts=["Dispatch recorded in city operational picture"],
                outcome_type="command",
            )
            return

        if isinstance(event, CrisisClassifiedEvent):
            inc = event.payload.get("incident", {})
            where = narr.sector(inc.get("location", ""))
            self.log_outcome(
                "Crisis playbook activated",
                f"All agents are coordinating on {inc.get('type', 'incident')} in {where}. "
                f"Expect dispatches, public advisories, and cascade warnings in sequence.",
                inc.get("confidence_score", 0.7),
                event.event_id,
                outcome_type="command",
            )
