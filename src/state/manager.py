import asyncio
from typing import Dict, List, Any
import copy
import logging
from datetime import datetime
from .models import GlobalStateModel, Incident, Resource

logger = logging.getLogger(__name__)

class StateManager:
    """
    Centralized Global State Manager.
    Holds the authoritative real-time state of the urban environment and incidents.
    Supports snapshots for timeline tracking and replay capabilities.
    """
    def __init__(self):
        # Active canonical state
        self._current_state = GlobalStateModel()
        
        # Timeline of historical state snapshots
        self._timeline: List[GlobalStateModel] = []
        
        # Async lock to prevent concurrent modifications during atomic updates
        self._lock = asyncio.Lock()

    async def get_state(self) -> GlobalStateModel:
        """Get a copy of the current state for read operations."""
        async with self._lock:
            # We return a deepcopy to ensure readers don't accidentally mutate state directly
            return copy.deepcopy(self._current_state)

    async def update_incident(self, incident: Incident) -> None:
        """Update or add an incident to the global state."""
        async with self._lock:
            self._current_state.active_incidents[incident.incident_id] = incident
            logger.debug(f"Incident {incident.incident_id} updated in state.")

    async def update_resource(self, resource: Resource) -> None:
        """Update or add a resource in the global state."""
        async with self._lock:
            self._current_state.resources[resource.resource_id] = resource
            logger.debug(f"Resource {resource.resource_id} updated in state.")
            
    async def update_crisis_confidence(self, score: float) -> None:
        """Update the global overarching crisis confidence score."""
        async with self._lock:
            self._current_state.crisis_confidence = max(0.0, min(1.0, score))

    async def create_snapshot(self, current_time: datetime) -> None:
        """Record the current state to the timeline."""
        async with self._lock:
            snapshot = copy.deepcopy(self._current_state)
            snapshot.timestamp = current_time
            self._timeline.append(snapshot)
            logger.debug(f"Created state snapshot at {current_time}.")

    async def rollback(self, target_time: datetime) -> bool:
        """
        Revert the state to the nearest snapshot prior to or at `target_time`.
        Useful for branching simulations or resolving conflicting data streams.
        """
        async with self._lock:
            if not self._timeline:
                return False
                
            # Find the latest snapshot <= target_time
            valid_snapshots = [s for s in self._timeline if s.timestamp <= target_time]
            if not valid_snapshots:
                return False
                
            # Grab the closet one
            closest_snapshot = sorted(valid_snapshots, key=lambda s: s.timestamp)[-1]
            
            # Prune the timeline of states after the rollback point
            self._timeline = [s for s in self._timeline if s.timestamp <= closest_snapshot.timestamp]
            
            self._current_state = copy.deepcopy(closest_snapshot)
            logger.warning(f"State rolled back to snapshot at {closest_snapshot.timestamp}.")
            return True
            
    def get_timeline(self) -> List[GlobalStateModel]:
        """Retrieve the historical snapshots."""
        return self._timeline
