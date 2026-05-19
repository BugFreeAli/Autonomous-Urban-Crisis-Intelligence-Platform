import logging
from typing import List, Dict, Any
from datetime import datetime

from ..state.models import GlobalStateModel, Incident, IncidentStatus

logger = logging.getLogger(__name__)

class MessagePayload:
    def __init__(self, stakeholder: str, channel: str, priority: str, message: str):
        self.stakeholder = stakeholder
        self.channel = channel
        self.priority = priority
        self.message = message
        self.timestamp = datetime.utcnow()

class StakeholderMessagingEngine:
    """
    Adaptive stakeholder communication and operational messaging system.
    Generates role-specific messaging and dynamic advisories.
    """
    def __init__(self):
        self.stakeholders = ["Public", "EmergencyServices", "Hospitals", "Utilities", "Transport", "Command"]

    def generate_briefs(self, event_type: str, state: GlobalStateModel, context: Dict[str, Any]) -> List[MessagePayload]:
        messages = []
        
        if event_type == "IncidentRetracted":
            inc_id = context.get("incident_id")
            messages.append(MessagePayload(
                stakeholder="Public",
                channel="Social/SMS",
                priority="Medium",
                message=f"[CORRECTION] Earlier reports of an incident ({inc_id}) have been invalidated. No threat detected. Normal activities may resume."
            ))
            messages.append(MessagePayload(
                stakeholder="Command",
                channel="Dashboard",
                priority="Low",
                message=f"Alert retracted for incident {inc_id} due to verification collapse."
            ))
            
        elif event_type == "CascadePredicted":
            loc = context.get("location")
            preds = context.get("predictions", [])
            messages.append(MessagePayload(
                stakeholder="Hospitals",
                channel="HealthNet",
                priority="High",
                message=f"[WARNING] Cascading failure projected near {loc}. Prepare for probable patient surge within 30-45 minutes. Initiate reserve capacity protocols."
            ))
            messages.append(MessagePayload(
                stakeholder="Transport",
                channel="TrafficOps",
                priority="High",
                message=f"Cascade projection indicates high risk of critical gridlock at {loc}. Begin preemptive rerouting of public transit."
            ))
            
        elif event_type == "CrisisClassified":
            inc = None
            if "incident" in context and isinstance(context["incident"], dict):
                raw = context["incident"]
                inc_id = raw.get("incident_id")
                inc = state.active_incidents.get(inc_id) if inc_id else None
                if not inc:
                    from ..state.models import Incident
                    try:
                        inc = Incident(**raw)
                    except Exception:
                        pass
            else:
                inc_id = context.get("incident_id")
                inc = state.active_incidents.get(inc_id) if inc_id else None
            if not inc:
                return []
                
            if inc.severity > 0.8:
                messages.append(MessagePayload(
                    stakeholder="Public",
                    channel="EAS/SMS",
                    priority="Critical",
                    message=f"[EMERGENCY ALERT] Severe {inc.type} confirmed at {inc.location}. Evacuate immediately if in the highlighted zone. Avoid all travel."
                ))
                messages.append(MessagePayload(
                    stakeholder="EmergencyServices",
                    channel="Dispatch",
                    priority="Critical",
                    message=f"Critical {inc.type} confirmed at {inc.location}. Severity: {inc.severity:.2f}. Execute Stage 3 Operational Response."
                ))
            else:
                messages.append(MessagePayload(
                    stakeholder="Public",
                    channel="Social/App",
                    priority="Low",
                    message=f"Advisory: Unconfirmed reports of {inc.type} near {inc.location}. Stay alert."
                ))
                
        elif event_type == "ResourceDispatched":
            messages.append(MessagePayload(
                stakeholder="Command",
                channel="Dashboard",
                priority="Medium",
                message=f"Unit {context.get('resource_id')} dispatched to {context.get('target_location')}. ETA: {context.get('eta')}s."
            ))

        return messages
