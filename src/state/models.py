from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class IncidentStatus(str, Enum):
    EMERGING = "Emerging"
    SUSPECTED = "Suspected"
    PROBABLE = "Probable"
    CONFIRMED = "Confirmed"
    ESCALATING = "Escalating"
    STABILIZED = "Stabilized"
    RESOLVED = "Resolved"
    RETRACTED = "Retracted"

class DistrictState(BaseModel):
    district_id: str
    name: str
    population: int
    vulnerability_index: float = Field(ge=0.0, le=1.0)
    traffic_density: float = Field(default=0.1, ge=0.0, le=1.0) # 1.0 = gridlock
    infrastructure_stress: float = Field(default=0.0, ge=0.0, le=1.0) # Power/Water risk
    weather_severity: float = Field(default=0.0, ge=0.0, le=1.0)

class HospitalState(BaseModel):
    hospital_id: str
    name: str
    district_id: str
    capacity: int
    current_load: int = 0
    surge_probability: float = 0.0

class Incident(BaseModel):
    incident_id: str
    type: str
    severity: float = Field(ge=0.0, le=1.0) # Normalizing to 0.0 - 1.0
    location: str # Could be district_id or coordinates
    reported_at: datetime
    status: IncidentStatus = IncidentStatus.EMERGING
    confidence_score: float = Field(ge=0.0, le=1.0)
    radius_meters: float = 100.0
    signals_clustered: int = 0
    contradiction_flag: bool = False
    prediction_tags: List[str] = Field(default_factory=list)

class Resource(BaseModel):
    resource_id: str
    type: str
    capacity: int
    status: str = "Available" # Available, Dispatched, On-Scene, Cooldown
    target_location: Optional[str] = None
    location: Optional[str] = None
    eta_seconds: Optional[int] = 0

class GlobalStateModel(BaseModel):
    """Represents the entire global view at a point in time."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    active_incidents: Dict[str, Incident] = Field(default_factory=dict)
    resources: Dict[str, Resource] = Field(default_factory=dict)
    districts: Dict[str, DistrictState] = Field(default_factory=dict)
    hospitals: Dict[str, HospitalState] = Field(default_factory=dict)
    crisis_confidence: float = Field(default=0.0, description="Overall system crisis level 0-1")
    simulation_mode: bool = False

