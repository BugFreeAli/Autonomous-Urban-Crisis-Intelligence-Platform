import asyncio
import logging
from typing import Callable, Awaitable, Dict, List, Set, Type
from .events import BaseEvent, EventPriority

logger = logging.getLogger(__name__)

# Type alias for an async event handler callback
EventHandler = Callable[[BaseEvent], Awaitable[None]]

class EventBus:
    """
    Centralized asynchronous event bus for routing events to subscribed agents and components.
    Prioritizes events via asyncio.PriorityQueue.
    """
    def __init__(self):
        # We use a PriorityQueue to ensure high-priority events are processed first.
        # Elements are tuples: (priority_value, timestamp, event) to break priority ties.
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        # Mapping of Event classes to a set of handler functions
        self._subscribers: Dict[Type[BaseEvent], Set[EventHandler]] = {}
        # Stores all published events for potential replay or analysis
        self._history: List[BaseEvent] = []
        self._processing_task: asyncio.Task | None = None
        self._is_running = False

    def subscribe(self, event_type: Type[BaseEvent], handler: EventHandler) -> None:
        """Subscribe an async handler to a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        self._subscribers[event_type].add(handler)
        logger.debug(f"Subscribed {handler.__name__} to {event_type.__name__}")

    def unsubscribe(self, event_type: Type[BaseEvent], handler: EventHandler) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].discard(handler)

    async def publish(self, event: BaseEvent) -> None:
        """Publish an event to the bus."""
        self._history.append(event)
        
        # Lower priority integer means higher priority in PriorityQueue
        # EventPriority values: LOW=1, MEDIUM=2, HIGH=3, CRITICAL=4
        # We want CRITICAL (4) to have the lowest sort value, so we use: -priority
        priority_sort = -event.priority.value
        
        await self._queue.put((priority_sort, event.timestamp, event))
        logger.debug(f"Published event: {event.event_id} of type {type(event).__name__}")

    async def _process_events(self) -> None:
        """Background loop to route events from the queue to subscribers."""
        while self._is_running:
            try:
                _, _, event = await self._queue.get()
                await self._route_event(event)
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")

    async def _route_event(self, event: BaseEvent) -> None:
        """Route a single event to all its subscribers concurrently."""
        event_type = type(event)
        handlers = self._subscribers.get(event_type, set())
        
        if not handlers:
            logger.debug(f"No subscribers for {event_type.__name__}")
            return

        # Execute all handlers concurrently for this event
        tasks = [asyncio.create_task(handler(event)) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)

    def start(self) -> None:
        """Start the event processing loop."""
        if not self._is_running:
            self._is_running = True
            self._processing_task = asyncio.create_task(self._process_events())
            logger.info("Event Bus started.")

    async def stop(self) -> None:
        """Stop processing and wait for the queue to empty."""
        if self._is_running:
            self._is_running = False
            if self._processing_task:
                self._processing_task.cancel()
                try:
                    await self._processing_task
                except asyncio.CancelledError:
                    pass
            logger.info("Event Bus stopped.")
            
    def get_history(self) -> List[BaseEvent]:
        """Hook to access event history, useful for replays."""
        return self._history
