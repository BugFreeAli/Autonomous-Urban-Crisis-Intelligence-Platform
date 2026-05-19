import abc
import uuid
from typing import Set, Type
from ..orchestration.event_bus import EventBus
from ..orchestration.events import BaseEvent
from ..state.manager import StateManager
from ..traces.logger import TraceLogger

class BaseAgent(abc.ABC):
    """
    Abstract base class for all autonomous agents in the system.
    Provides foundational capabilities for event subscription, state access, and trace logging.
    """
    def __init__(
        self, 
        event_bus: EventBus, 
        state_manager: StateManager,
        trace_logger: TraceLogger,
        agent_name: str,
        intelligence_engine = None
    ):
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.trace_logger = trace_logger
        self.agent_name = agent_name
        self.intelligence_engine = intelligence_engine
        self.subscribed_events: Set[Type[BaseEvent]] = set()

    def subscribe(self, event_type: Type[BaseEvent]) -> None:
        """Register the agent to handle a specific event type."""
        self.event_bus.subscribe(event_type, self.handle_event)
        self.subscribed_events.add(event_type)

    async def handle_event(self, event: BaseEvent) -> None:
        """
        Generic entry point for incoming events from the Event Bus.
        Routes to the abstract process_event method which subclasses must implement.
        """
        # Note: In a more complex setup, you might map specific event types 
        # to specific handler methods via decorators, but a single entry point 
        # is fine for the foundation.
        await self.process_event(event)

    @abc.abstractmethod
    async def process_event(self, event: BaseEvent) -> None:
        """Core reasoning logic loop to be implemented by specific agents."""
        pass
        
    async def emit_decision(self, event: BaseEvent) -> None:
        """Publish a new resulting event/decision back to the bus."""
        await self.event_bus.publish(event)
        
    def log_reasoning(
        self,
        action_type: str,
        reasoning: str,
        confidence_score: float,
        trigger_event_id: str = None,
        trade_offs: list = None,
        metadata: dict = None,
    ) -> None:
        """Internal reasoning shown in the Agent Reasoning terminal."""
        meta = {"display_kind": "reasoning", **(metadata or {})}
        trace_id = str(uuid.uuid4())
        self.trace_logger.log_decision(
            trace_id=trace_id,
            agent_name=self.agent_name,
            action_type=action_type,
            reasoning=reasoning,
            confidence_score=confidence_score,
            trigger_event_id=trigger_event_id,
            trade_offs=trade_offs,
            metadata=meta,
        )

    def log_outcome(
        self,
        headline: str,
        what_we_did: str,
        confidence_score: float,
        trigger_event_id: str = None,
        impacts: list = None,
        outcome_type: str = "action",
    ) -> None:
        """Final decision / action — shown prominently on the Operations tab."""
        body = what_we_did
        if impacts:
            body += "\n\nResults:\n" + "\n".join(f"• {line}" for line in impacts)
        trace_id = str(uuid.uuid4())
        self.trace_logger.log_decision(
            trace_id=trace_id,
            agent_name=self.agent_name,
            action_type="OperationalOutcome",
            reasoning=f"{headline}\n\n{body}",
            confidence_score=confidence_score,
            trigger_event_id=trigger_event_id,
            trade_offs=impacts or [],
            metadata={
                "display_kind": "outcome",
                "headline": headline,
                "outcome_type": outcome_type,
            },
        )
