from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum

class EventPriority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class BaseEvent(BaseModel):
    """Base model for all events in the system."""
    event_id: str = Field(..., description="Unique identifier for the event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time the event occurred")
    source: str = Field(..., description="Origin of the event (agent name, system component, external sensor)")
    priority: EventPriority = Field(default=EventPriority.MEDIUM, description="Priority of the event")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")

    class Config:
        arbitrary_types_allowed = True


# Example Domain Events

class SocialSignalEvent(BaseEvent):
    """Citizen reports, social media posts. High volume, variable credibility."""
    pass

class WeatherUpdateEvent(BaseEvent):
    """Dynamic weather propagation (rainfall, heatwave)."""
    pass

class TrafficUpdateEvent(BaseEvent):
    """Congestion spikes, road closures."""
    pass

class FieldReportEvent(BaseEvent):
    """Verified or contradictory reports from utility/emergency crews."""
    pass

class HospitalUpdateEvent(BaseEvent):
    """Dynamic ER capacity, surges, resource limitations."""
    pass

class BaseSignalDetected(BaseEvent): pass
class RainfallDetected(BaseSignalDetected): pass
class TrafficSpikeDetected(BaseSignalDetected): pass
class FloodSignalDetected(BaseSignalDetected): pass
class HospitalLoadIncreased(BaseSignalDetected): pass
class ResourceDispatched(BaseSignalDetected): pass

# --- Inter-Agent Communication Events ---

class IncidentHypothesisEvent(BaseEvent):
    """Emitted by Signal/Fusion Agent when raw signals cluster into a suspected anomaly."""
    pass

class CredibilityVerifiedEvent(BaseEvent):
    """Emitted after Credibility agent assesses source veracity and contradictions."""
    pass

class ContradictionDetectedEvent(BaseEvent):
    """Emitted when conflicting reports are identified."""
    pass

class CrisisClassifiedEvent(BaseEvent):
    """Emitted when an incident is fully classified and confidence updated."""
    pass

class IncidentRetractedEvent(BaseEvent):
    """Emitted when an alert is retracted due to confidence collapse/false positive."""
    pass

class HumanVerificationEscalationEvent(BaseEvent):
    """Emitted when an incident is too ambiguous and needs human eyes."""
    pass

class IncidentMergedEvent(BaseEvent):
    """Emitted when duplicate incidents are merged."""
    pass

class CascadePredictedEvent(BaseEvent):
    """Emitted when the Cascade engine calculates future timeline ramifications."""
    pass


