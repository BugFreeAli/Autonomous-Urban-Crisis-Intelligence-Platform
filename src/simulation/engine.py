import asyncio
import logging
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..state.manager import StateManager
from ..state.models import DistrictState, HospitalState, Incident, Resource
from ..orchestration.event_bus import EventBus
from ..orchestration.events import (
    SocialSignalEvent, WeatherUpdateEvent, TrafficUpdateEvent, 
    FieldReportEvent, HospitalUpdateEvent, EventPriority
)

logger = logging.getLogger(__name__)

class CitySimulationEngine:
    """
    Realistic living urban simulation. 
    Continuously evolves city state based on active scenarios and cascading failures.
    """
    def __init__(self, state_manager: StateManager, event_bus: EventBus):
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.active_scenarios = []

    async def initialize_city(self):
        """Seed the global state with default districts, hospitals, and resources."""
        # Setup Mock Districts ( Downtown, Suburbs, Riverside )
        districts = [
            DistrictState(district_id="D1", name="Downtown", population=50000, vulnerability_index=0.4),
            DistrictState(district_id="D2", name="Riverside", population=20000, vulnerability_index=0.8),
            DistrictState(district_id="D3", name="Uptown", population=35000, vulnerability_index=0.2),
        ]
        hospitals = [
            HospitalState(hospital_id="H1", name="Metro General", district_id="D1", capacity=500, current_load=300),
            HospitalState(hospital_id="H2", name="Riverside Medical", district_id="D2", capacity=150, current_load=100),
        ]
        resources = [
            Resource(resource_id="A-1", type="Ambulance", capacity=2, location="D1", status="Available"),
            Resource(resource_id="A-2", type="Ambulance", capacity=2, location="D2", status="Available"),
            Resource(resource_id="ENG-1", type="FireEngine", capacity=5, location="D1", status="Available"),
            Resource(resource_id="UTIL-1", type="UtilityCrew", capacity=4, location="D3", status="Available"),
        ]

        state = await self.state_manager.get_state()
        for d in districts:
            state.districts[d.district_id] = d
        for h in hospitals:
            state.hospitals[h.hospital_id] = h
        for r in resources:
            state.resources[r.resource_id] = r
            
        async with self.state_manager._lock:
            self.state_manager._current_state = state
            
        logger.info("City initialized with default topology.")

    async def tick(self, current_time: datetime):
        """
        Called every simulation clock tick.
        Progresses models: traffic, hospitals, resources, and cascades.
        """
        state = await self.state_manager.get_state()
        state_updated = False
        
        # 1. Update Resources (Move them toward destinations, cooldowns)
        for res_id, res in state.resources.items():
            if res.status == "Dispatched" and res.eta_seconds > 0:
                # Based on traffic of their current location
                district_traffic = getattr(state.districts.get(res.location), 'traffic_density', 0.1)
                reduction = int(1 * (1.0 - (district_traffic * 0.5))) # Slower ETA reduction in heavy traffic
                res.eta_seconds = max(0, res.eta_seconds - reduction)
                
                if res.eta_seconds == 0:
                    res.status = "On-Scene"
                    res.location = res.target_location
                    state_updated = True
                    await self._emit_field_report(current_time, res)

        # 2. Evolve Scenarios & Incidents
        for inc_id, incident in state.active_incidents.items():
            if incident.status == "Active":
                # Incidents naturally expand unless heavily resourced
                assigned_resc = len([r for r in state.resources.values() if r.target_location == incident.location and r.status == "On-Scene"])
                if assigned_resc == 0:
                    incident.severity = min(1.0, incident.severity + 0.05) # Escalate rapidly
                    incident.radius_meters *= 1.05
                    state_updated = True
                elif assigned_resc > 2:
                    incident.severity = max(0.0, incident.severity - 0.05) # Stabilize
                    if incident.severity == 0.0:
                        incident.status = "Resolved"
                    state_updated = True
        
        # 3. Process Cascades (E.g. High severity in flood district = huge traffic = hospital overload)
        for dist_id, district in state.districts.items():
            # Find active incidents here
            local_incidents = [inc for inc in state.active_incidents.values() if inc.location == dist_id and inc.status == "Active"]
            base_stress = sum(inc.severity for inc in local_incidents)
            
            if base_stress > 0:
                # Congestion cascades
                old_traffic = district.traffic_density
                district.traffic_density = min(1.0, district.traffic_density + (base_stress * 0.1))
                if district.traffic_density - old_traffic > 0.1:
                    await self._emit_traffic_update(current_time, district)
                
                # Hospital Load Cascades
                hospitals_in_district = [h for h in state.hospitals.values() if h.district_id == dist_id]
                for h in hospitals_in_district:
                    old_load = h.current_load
                    h.current_load = min(h.capacity, int(h.current_load + (base_stress * 10 * district.population / 10000)))
                    h.surge_probability = h.current_load / sorted([h.capacity, 1])[1]
                    if (h.current_load - old_load) > 10:
                         await self._emit_hospital_surge(current_time, h)
                
                state_updated = True

        # Generate Ambient Misinformation/Social Noise
        if random.random() < 0.3:
             await self._emit_social_noise(current_time, state)

        # Snap the state back safely
        if state_updated:
            async with self.state_manager._lock:
                self.state_manager._current_state = state

    async def _emit_social_noise(self, current_time, state):
        credibility = random.uniform(0.1, 0.9)
        # Occasionally generate blatant misinformation
        if random.random() < 0.1:
            credibility = 0.05
            msg = "HEARING EXPLOSIONS DOWN BY RADIATOR HILL!"
        else:
            msg = "Traffic is completely jammed here."
            
        evt = SocialSignalEvent(
            event_id=f"soc-{str(uuid.uuid4())[:8]}",
            timestamp=current_time,
            source="SocialSim",
            payload={"message": msg, "credibility": credibility, "location": list(state.districts.keys())[0]},
            priority=EventPriority.LOW
        )
        await self.event_bus.publish(evt)

    async def _emit_traffic_update(self, current_time, district):
        evt = TrafficUpdateEvent(
            event_id=f"trf-{str(uuid.uuid4())[:8]}",
            timestamp=current_time,
            source="TrafficSim",
            payload={"district": district.name, "density": district.traffic_density},
            priority=EventPriority.MEDIUM
        )
        await self.event_bus.publish(evt)

    async def _emit_hospital_surge(self, current_time, hospital):
        evt = HospitalUpdateEvent(
            event_id=f"hsp-{str(uuid.uuid4())[:8]}",
            timestamp=current_time,
            source="HospitalSim",
            payload={"hospital": hospital.name, "load": hospital.current_load, "capacity": hospital.capacity, "surge_prob": hospital.surge_probability},
            priority=EventPriority.HIGH
        )
        await self.event_bus.publish(evt)

    async def _emit_field_report(self, current_time, resource):
        evt = FieldReportEvent(
            event_id=f"fld-{str(uuid.uuid4())[:8]}",
            timestamp=current_time,
            source=f"FieldRes-{resource.resource_id}",
            payload={"message": f"{resource.type} arrived on-scene at {resource.location}.", "resource": resource.resource_id},
            priority=EventPriority.HIGH
        )
        await self.event_bus.publish(evt)

    # --- Scenario Triggers ---
    
    async def trigger_flood_scenario(self, current_time: datetime):
        """Inject a high-severity flood scenario in Riverside causing immediate cascades."""
        incident = Incident(
            incident_id=f"inc-{uuid.uuid4()}",
            type="Severe Flooding",
            severity=0.7,
            location="D2",  # Riverside
            reported_at=current_time,
            confidence_score=0.9
        )
        await self.state_manager.update_incident(incident)
        logger.warning(f"SIMULATION ENGINE: Triggered Flood Scenario in D2 (Riverside).")
        
        # Immediate dynamic signal
        evt = WeatherUpdateEvent(
            event_id=f"wx-{uuid.uuid4()}",
            timestamp=current_time,
            source="WxSim",
            payload={"alert": "Flash Flood Warning", "rainfall_mm": 50},
            priority=EventPriority.CRITICAL
        )
        await self.event_bus.publish(evt)
