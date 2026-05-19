import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
import uuid

from ..state.models import GlobalStateModel, Incident, IncidentStatus

logger = logging.getLogger(__name__)

class VerificationResult:
    def __init__(self, incident_id: str, final_confidence: float, action: str, reasoning_trace: List[str], requires_human: bool = False, merge_target: str = None):
        self.incident_id = incident_id
        self.final_confidence = final_confidence
        self.action = action # "CONFIRM", "RETRACT", "ESCALATE_HUMAN", "MERGE", "DECAY"
        self.reasoning_trace = reasoning_trace
        self.requires_human = requires_human
        self.merge_target = merge_target

class VerificationEngine:
    """
    Adaptive verification, contradiction handling, and recovery engine.
    Applies logic to upgrade, merge, or retract suspected incidents based on signal credibility.
    """
    def __init__(self):
        self.stale_data_threshold_seconds = 600 # 10 minutes

    def evaluate_hypothesis(self, payload: Dict[str, Any], state: GlobalStateModel) -> VerificationResult:
        """
        Evaluate a new or existing incident hypothesis.
        Applies contradiction analysis, credibility scoring, and incident merging.
        """
        trace = []
        loc = payload.get("location", "Unknown")
        signal_count = payload.get("signal_count", 1)
        raw_creds = payload.get("raw_credibilities", [0.5])
        suspected_type = payload.get("suspected_type", "Unknown")
        target_incident_id = payload.get("incident_id", f"inc-{uuid.uuid4().hex[:8]}")
        
        # 1. Base Credibility Scoring
        base_cred = sum(raw_creds) / len(raw_creds) if raw_creds else 0.5
        trace.append(f"Average trust in incoming reports is {base_cred:.0%}.")

        # 2. Confidence Decay / Stale Data Check
        timestamp = payload.get("timestamp")
        # In a real app we parse actual datetime
        # For simulation, just assume fresh unless explicitly marked old
        if payload.get("is_stale", False) or base_cred < 0.2:
            base_cred *= 0.8
            trace.append("Reports look stale or very weak — I reduced how much I trust them.")

        # 3. Duplicate / Incident Merging Detection
        # Check if identical incident type strongly overlapping
        active_incidents = state.active_incidents.values()
        merge_target_id = None
        for inc in active_incidents:
            if inc.location == loc and inc.type == suspected_type and inc.status not in [IncidentStatus.RESOLVED, IncidentStatus.RETRACTED]:
                # Found overlap
                merge_target_id = inc.incident_id
                trace.append(f"This matches an open incident ({inc.incident_id}) in the same area — likely the same event.")
                break

        if merge_target_id:
            return VerificationResult(
                incident_id=target_incident_id,
                final_confidence=base_cred +0.1,
                action="MERGE",
                reasoning_trace=trace,
                merge_target=merge_target_id
            )

        # 4. Contradiction Analysis & Misinformation Handling
        contradiction = False
        requires_human = False
        action = "CONFIRM"
        final_confidence = min(1.0, base_cred + (signal_count * 0.05))

        if signal_count > 10 and base_cred < 0.3:
            contradiction = True
            trace.append("Many posts, but almost none are trustworthy — looks like a bot swarm or hoax.")
        
        if suspected_type == "Flood" and "Weather" not in payload.get("sensor_data", []):
            contradiction = True
            trace.append("People claim flooding, but weather sensors do not support it.")

        # 5. False Positive & Retraction
        if contradiction:
            final_confidence -= 0.5 # Massive hit
            if final_confidence < 0.3:
                action = "RETRACT"
                trace.append(f"Confidence fell to {final_confidence:.0%} — treating this as a false alarm.")
            else:
                action = "ESCALATE_HUMAN"
                requires_human = True
                trace.append("Reports conflict — a human operator should decide before we act.")
        else:
            trace.append(f"Reports are consistent enough — confidence is now {final_confidence:.0%}.")

        if final_confidence > 0.8:
            action = "CONFIRM"

        return VerificationResult(
            incident_id=target_incident_id,
            final_confidence=max(0.0, final_confidence),
            action=action,
            reasoning_trace=trace,
            requires_human=requires_human
        )
