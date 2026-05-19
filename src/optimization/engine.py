import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
import uuid

from ..state.models import GlobalStateModel, Resource, Incident, HospitalState, DistrictState

logger = logging.getLogger(__name__)

class OptimizationAction:
    def __init__(self, resource_id: str, target_location: str, action_type: str, estimated_eta: int, trade_offs: List[str]):
        self.resource_id = resource_id
        self.target_location = target_location
        self.action_type = action_type # e.g., "Dispatch", "Reroute", "Hold_Reserve"
        self.estimated_eta = estimated_eta
        self.trade_offs = trade_offs

class ResourceOptimizationEngine:
    """
    Predictive Autonomous Resource Optimization Engine.
    Dynamically allocates constrained emergency resources across simultaneous crises.
    Optimizes for response time, casualty reduction, hospital stability, and reserve preservation.
    """
    def __init__(self):
        # A simple simulated distance map for ETA calculation
        # In a real app, this would use OSRM or a real routing engine.
        pass

    def _estimate_eta(self, start_loc: str, end_loc: str, state: GlobalStateModel) -> int:
        """Estimate travel time in seconds, factoring in target traffic density."""
        base_time = 300 if start_loc != end_loc else 60 # 5 mins between districts, 1 min within
        target_district = state.districts.get(end_loc)
        traffic_mult = 1.0 + (target_district.traffic_density * 2.0 if target_district else 0.0)
        return int(base_time * traffic_mult)

    def optimize_allocation(self, state: GlobalStateModel, predictions: List[Dict[str, Any]] = None) -> Tuple[List[OptimizationAction], float, List[str]]:
        """
        Calculates optimal allocation of currently available resources.
        Returns a list of OptimizationActions, an overall confidence score, and high-level reasoning.
        """
        actions = []
        reasoning_chain = []
        
        active_incidents = [inc for inc in state.active_incidents.values() if inc.status in ["Emerging", "Suspected", "Probable", "Confirmed", "Escalating"]]
        available_resources = [r for r in state.resources.values() if r.status == "Available"]
        
        total_available = len(available_resources)
        reserve_threshold = max(1, int(total_available * 0.2)) # Keep 20% in reserve if possible minimum 1
        
        # Sort incidents by severity
        active_incidents.sort(key=lambda x: x.severity, reverse=True)
        
        if not active_incidents:
            return [], 1.0, ["No active incidents require optimization."]

        allocated_resources = set()

        # Phase 1: High Severity & Hospital Protection
        for incident in active_incidents:
            if len(available_resources) - len(allocated_resources) <= reserve_threshold and incident.severity < 0.8:
                reasoning_chain.append(f"Preserving reserves. Skipping low-severity incident at {incident.location}.")
                continue

            # Need to assign resources based on incident type
            needed_types = ["Ambulance", "Police", "FireEngine", "UtilityCrew", "Drone"]
            
            for r_type in needed_types:
                # Find available resources of this type not yet allocated
                candidates = [r for r in available_resources if r.type == r_type and r.resource_id not in allocated_resources]
                if not candidates:
                    continue

                # Sort by ETA
                candidates.sort(key=lambda r: self._estimate_eta(r.location, incident.location, state))
                best_candidate = candidates[0]
                
                eta = self._estimate_eta(best_candidate.location, incident.location, state)
                
                trade_offs = [
                    f"Reduced reserve for {r_type} to {len(candidates)-1} units.",
                    f"ETA penalty: {eta}s due to current traffic conditions."
                ]
                
                actions.append(OptimizationAction(
                    resource_id=best_candidate.resource_id,
                    target_location=incident.location,
                    action_type="Dispatch",
                    estimated_eta=eta,
                    trade_offs=trade_offs
                ))
                
                allocated_resources.add(best_candidate.resource_id)
                reasoning_chain.append(f"Allocated {best_candidate.type} ({best_candidate.resource_id}) to {incident.location} for incident {incident.type}.")
                
                # Stop if we've assigned 2 resources to this incident to spread them out
                assigned_to_this = len([a for a in actions if a.target_location == incident.location])
                if assigned_to_this >= 2:
                    break

        confidence = 0.85
        if len(available_resources) - len(allocated_resources) == 0:
            confidence = 0.60
            reasoning_chain.append("CRITICAL: All reserves exhausted. High risk for cascading failures.")

        return actions, confidence, reasoning_chain

