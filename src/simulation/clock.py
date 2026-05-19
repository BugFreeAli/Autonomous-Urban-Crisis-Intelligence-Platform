import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Awaitable, List

logger = logging.getLogger(__name__)

class SimulationClock:
    """
    Manages the simulation time which can be accelerated or synchronized with real-time.
    Useful for future prediction roll-outs and replay testing.
    """
    def __init__(self, start_time: datetime, time_scale_factor: float = 1.0):
        self._start_time_real = datetime.utcnow()
        self._start_time_sim = start_time
        
        # Factor for how fast simulation time passes relative to real time.
        # 1.0 = real-time, 60.0 = one hour simulation per one minute real-time
        self.time_scale_factor = time_scale_factor
        
        self._is_running = False
        self._tick_task: asyncio.Task | None = None
        
        # Subscribed callbacks for periodic ticks (e.g. state snapshotting)
        self._tick_callbacks: List[Callable[[datetime], Awaitable[None]]] = []
        
        # Future scheduled events: list of (sim_time, callback)
        self._scheduled_events: List[tuple[datetime, Callable[[], Awaitable[None]]]] = []
        
        # Controls tick interval in real seconds (determines granularity of scheduled events)
        self._real_tick_interval = 1.0 

    @property
    def current_time(self) -> datetime:
        """Calculate the current simulation time based on scale and elapsed real time."""
        if not self._is_running:
            # If not running, return the time it would be if paused exactly here
            return self._start_time_sim
            
        real_elapsed = datetime.utcnow() - self._start_time_real
        sim_elapsed_seconds = real_elapsed.total_seconds() * self.time_scale_factor
        return self._start_time_sim + timedelta(seconds=sim_elapsed_seconds)

    def register_tick_callback(self, callback: Callable[[datetime], Awaitable[None]]):
        """Register a callback to be fired on every clock tick."""
        self._tick_callbacks.append(callback)
        
    def schedule_future_event(self, trigger_time: datetime, callback: Callable[[], Awaitable[None]]):
        """Schedule a callback to be executed when the simulation time reaches trigger_time."""
        self._scheduled_events.append((trigger_time, callback))
        # Sort so we can easily pop upcoming ones
        self._scheduled_events.sort(key=lambda x: x[0], reverse=True)

    async def _tick_loop(self):
        """Internal loop ticking the clock and triggering callbacks."""
        while self._is_running:
            await asyncio.sleep(self._real_tick_interval)
            current_sim_time = self.current_time
            
            # Fire all scheduled callbacks
            if self._tick_callbacks:
                tasks = [asyncio.create_task(cb(current_sim_time)) for cb in self._tick_callbacks]
                await asyncio.gather(*tasks, return_exceptions=True)
                
            # Fire future scheduled events that are ready
            ready_events = []
            # _scheduled_events is sorted descending, so last element is the earliest time
            while self._scheduled_events and self._scheduled_events[-1][0] <= current_sim_time:
                ready_events.append(self._scheduled_events.pop()[1])
                
            if ready_events:
                event_tasks = [asyncio.create_task(cb()) for cb in ready_events]
                await asyncio.gather(*event_tasks, return_exceptions=True)

    def start(self):
        """Start the simulation clock."""
        if not self._is_running:
            self._start_time_real = datetime.utcnow() # Reset real start for the interval
            self._is_running = True
            self._tick_task = asyncio.create_task(self._tick_loop())
            logger.info(f"Simulation Clock started at {self._start_time_sim} (Scale {self.time_scale_factor}x)")

    async def stop(self):
        """Stop the simulation clock."""
        if self._is_running:
            self._is_running = False
            if self._tick_task:
                self._tick_task.cancel()
                try:
                    await self._tick_task
                except asyncio.CancelledError:
                    pass
            logger.info(f"Simulation Clock stopped at {self.current_time}.")
            # Store the current time back so if restarted, it resumes from the paused sim time
            self._start_time_sim = self.current_time
