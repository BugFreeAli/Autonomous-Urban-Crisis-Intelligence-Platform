import logging
from typing import List
from ..orchestration.event_bus import EventBus
from ..state.manager import StateManager
from ..traces.logger import TraceLogger
from ..agents.base import BaseAgent
from ..agents.implementations import (
    SignalIntelligenceAgent, CredibilityAgent, CrisisClassificationAgent,
    CascadePredictionAgent, ResourceOptimizationAgent, SimulationAgent,
    RecoveryAgent, StakeholderCommunicationAgent, CentralCommandAgent
)

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Initializes and manages the lifecycle of the multi-agent system,
    wiring them to the central Event Bus and State Manager.
    """
    def __init__(self, event_bus: EventBus, state_manager: StateManager, trace_logger: TraceLogger, intelligence_engine=None):
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.trace_logger = trace_logger
        self.intelligence_engine = intelligence_engine
        self.agents: List[BaseAgent] = []

    def initialize_agents(self) -> None:
        """Instantiate all agents and register their subscriptions."""
        logger.info("Initializing multi-agent network...")
        
        agent_params = {
            "event_bus": self.event_bus,
            "state_manager": self.state_manager,
            "trace_logger": self.trace_logger
        }
        
        # Add intelligence engine to params if provided
        if self.intelligence_engine:
            agent_params["intelligence_engine"] = self.intelligence_engine

        agent_classes = [
            SignalIntelligenceAgent,
            CredibilityAgent,
            CrisisClassificationAgent,
            CascadePredictionAgent,
            ResourceOptimizationAgent,
            SimulationAgent,
            RecoveryAgent,
            StakeholderCommunicationAgent,
            CentralCommandAgent
        ]
        
        for cls in agent_classes:
            agent_instance = cls(**agent_params)
            self.agents.append(agent_instance)
            logger.debug(f"Initialized {agent_instance.agent_name}")
            
        logger.info(f"Successfully booted {len(self.agents)} agents.")
