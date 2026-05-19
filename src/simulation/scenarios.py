import asyncio
import logging
import random
import uuid
from datetime import datetime
from typing import Dict, Any

from .engine import CitySimulationEngine
from ..orchestration.event_bus import EventBus
from ..orchestration.events import (
    SocialSignalEvent, WeatherUpdateEvent, TrafficUpdateEvent, 
    FieldReportEvent, EventPriority
)

logger = logging.getLogger(__name__)

class CinematicScenarioRunner:
    """
    Executes advanced stress-testing scenarios and cinematic operational demo flows.
    Designed for judge impact, storytelling, and demonstrating autonomous AI reasoning.
    """
    def __init__(self, engine: CitySimulationEngine, event_bus: EventBus):
        self.engine = engine
        self.event_bus = event_bus

    async def run_simultaneous_flood_heatwave(self, start_time: datetime):
        """
        SCENARIO 1: Simultaneous Flood + Heatwave
        Demonstrates the Cascade Engine managing competing multi-variant crises.
        """
        logger.info("CINEMATIC: Starting Simultaneous Flood + Heatwave Scenario")
        
        # 1. Start with a baseline Heatwave in Downtown
        await self.event_bus.publish(WeatherUpdateEvent(
            event_id=f"wx-{uuid.uuid4()}", timestamp=start_time, source="NOAA_API",
            priority=EventPriority.HIGH, payload={"location": "Downtown", "alert": "Severe Heatwave", "temp_c": 42.0}
        ))
        await asyncio.sleep(1.0)
        
        # 2. Power Grid stress signals
        for _ in range(3):
            await self.event_bus.publish(SocialSignalEvent(
                event_id=f"soc-{uuid.uuid4()}", timestamp=start_time, source="Twitter",
                priority=EventPriority.MEDIUM, payload={"location": "Downtown", "text": "Power just went out!", "credibility": 0.85}
            ))

        # 3. Sudden Flash Flood in Riverside (Constraining resources)
        await asyncio.sleep(2.0)
        await self.event_bus.publish(WeatherUpdateEvent(
            event_id=f"wx-{uuid.uuid4()}", timestamp=start_time, source="CitySensor_Hydro",
            priority=EventPriority.CRITICAL, payload={"location": "Riverside", "alert": "Levee Breach", "water_level_m": 1.5}
        ))
        
        for _ in range(4):
            await self.event_bus.publish(SocialSignalEvent(
                event_id=f"soc-{uuid.uuid4()}", timestamp=start_time, source="TikTok",
                priority=EventPriority.HIGH, payload={"location": "Riverside", "text": "Streets are flooding fast, need rescue", "credibility": 0.9}
            ))
            
    async def run_contradictory_reports(self, start_time: datetime):
        """
        SCENARIO 2: Contradictory Flooding Reports (Misinformation / False Alarm)
        Demonstrates the Validity/Credibility agent dynamically collapsing confidence and retracting.
        """
        logger.info("CINEMATIC: Starting Contradictory Reports Scenario")
        
        # 1. Massive influx of social signals (Bot swarm simulation)
        for _ in range(12):
            await self.event_bus.publish(SocialSignalEvent(
                event_id=f"soc-{uuid.uuid4()}", timestamp=start_time, source="AnonymousApp",
                priority=EventPriority.MEDIUM, payload={"location": "Uptown", "text": "Huge gas explosion! Fire everywhere!", "credibility": 0.15}
            ))
            
        await asyncio.sleep(2.0)
        
        # 2. Hard sensors contradict
        await self.event_bus.publish(FieldReportEvent(
            event_id=f"fld-{uuid.uuid4()}", timestamp=start_time, source="Drone-04",
            priority=EventPriority.HIGH, payload={"location": "Uptown", "message": "Visual scan negative. No fire detected. Baseline normal."}
        ))
        
        # System should auto-retract after human verification / contradiction limits

    async def run_hospital_overload_escalation(self, start_time: datetime):
        """
        SCENARIO 4: Hospital Overload Escalation (Resource Exhaustion Prep)
        Demonstrates proactive rerouting and predictive cascade graphs.
        """
        logger.info("CINEMATIC: Starting Hospital Overload Escalation")
        
        # Spike traffic to slow down ambulances
        await self.event_bus.publish(TrafficUpdateEvent(
            event_id=f"trf-{uuid.uuid4()}", timestamp=start_time, source="TrafficCams",
            priority=EventPriority.HIGH, payload={"location": "Downtown", "density": 0.95, "message": "Gridlock on major arteries."}
        ))
        
        await asyncio.sleep(1.0)
        # Multi-vehicle pileup
        for _ in range(5):
            await self.event_bus.publish(SocialSignalEvent(
                event_id=f"soc-{uuid.uuid4()}", timestamp=start_time, source="Waze",
                priority=EventPriority.HIGH, payload={"location": "Downtown", "text": "Massive pileup, multiple injuries.", "credibility": 0.90}
            ))

    async def run_evacuation_spiral(self, start_time: datetime):
        """
        SCENARIO 5: Evacuation Congestion Spiral
        Demonstrates 2nd and 3rd order effect cascading.
        """
        logger.info("CINEMATIC: Starting Evacuation Congestion Spiral")
        # Trigger chemical hazmat warning
        await self.event_bus.publish(SocialSignalEvent(
            event_id=f"soc-{uuid.uuid4()}", timestamp=start_time, source="CitizenApp",
            priority=EventPriority.HIGH, payload={"location": "Riverside", "text": "Yellow smoke from the factory, eyes burning", "credibility": 0.8}
        ))
        await self.event_bus.publish(SocialSignalEvent(
            event_id=f"soc-{uuid.uuid4()}", timestamp=start_time, source="CitizenApp",
            priority=EventPriority.HIGH, payload={"location": "Riverside", "text": "Chemical smell, people running", "credibility": 0.88}
        ))

    async def run_resource_exhaustion(self, start_time: datetime):
        """
        SCENARIO 7: Resource Exhaustion
        Demonstrates the Resource Optimizer preserving reserve margins tightly.
        """
        logger.info("CINEMATIC: Starting Resource Exhaustion")
        # 10 separate minor incidents to drain resources, followed by 1 major critical event
        locations = ["Downtown", "Riverside", "Uptown"]
        for i in range(4):
            loc = random.choice(locations)
            await self.event_bus.publish(SocialSignalEvent(
                event_id=f"soc-{uuid.uuid4()}", timestamp=start_time, source="TrafficOps",
                priority=EventPriority.MEDIUM, payload={"location": loc, "text": f"Minor collision {i}", "credibility": 0.7}
            ))
            await asyncio.sleep(0.5)
            
        await asyncio.sleep(2.0)
        # Drop the Hammer
        await self.event_bus.publish(WeatherUpdateEvent(
            event_id=f"wx-{uuid.uuid4()}", timestamp=start_time, source="SeismicNet",
            priority=EventPriority.CRITICAL, payload={"location": "Downtown", "alert": "Earthquake Magnitude 6.2", "credibility": 1.0}
        ))

