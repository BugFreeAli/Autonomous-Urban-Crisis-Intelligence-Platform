from ..orchestration.event_bus import EventBus
from ..state.manager import StateManager
from ..traces.logger import TraceLogger
from ..simulation.clock import SimulationClock
from ..orchestration.orchestrator import AgentOrchestrator
from ..simulation.engine import CitySimulationEngine
from ..intelligence.engine import intelligence_engine
from datetime import datetime

# Global instances acting as crude Singletons for the FastAPI dependency injection.
# In a larger production app, you might use a more robust DI container (like dependency-injector)

event_bus = EventBus()
state_manager = StateManager()
trace_logger = TraceLogger()
sim_clock = SimulationClock(start_time=datetime.utcnow(), time_scale_factor=1.0)
orchestrator = AgentOrchestrator(event_bus, state_manager, trace_logger, intelligence_engine)
sim_engine = CitySimulationEngine(state_manager, event_bus)

def get_event_bus() -> EventBus:
    return event_bus

def get_state_manager() -> StateManager:
    return state_manager

def get_trace_logger() -> TraceLogger:
    return trace_logger

def get_sim_clock() -> SimulationClock:
    return sim_clock

def get_sim_engine() -> CitySimulationEngine:
    return sim_engine

def get_intelligence_engine():
    return intelligence_engine
