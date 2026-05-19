from pydantic import BaseModel, Field
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from ..state.models import GlobalStateModel, Incident, DistrictState, HospitalState

class PredictedConsequence(BaseModel):
    consequence_type: str        # e.g., "CongestionSpread", "HospitalOverload"
    description: str
    target_entity_id: str        # e.g., "D2" (District) or "H1" (Hospital)
    probability: float           # 0.0 - 1.0
    uncertainty_range: Tuple[float, float] # e.g., (0.6, 0.9)
    estimated_time: datetime     # When it is expected to hit critical mass
    severity_impact: float       # Predicted severity contribution

class CascadePredictionEngine:
    """
    Autonomous cascade prediction and consequence propagation engine.
    Traverses a defined dependency graph of urban mechanics to forecast
    secondary and tertiary consequences if no interventions occur.
    """
    
    # Graph representing causal links and their base transmission probabilities tracking outward
    # Format: Trigger -> [(Consequence, Base_Probability, Time_Delay_Mins, Severity_Multiplier)]
    DEPENDENCY_GRAPH = {
        "Severe Weather / Flooding": [
            ("Evacuation Congestion", 0.85, 10, 1.2),
            ("Secondary Accident", 0.60, 15, 0.8),
            ("Power Outage", 0.40, 30, 1.5)
        ],
        "Traffic Collapse": [
            ("Ambulance Delay", 0.95, 5, 1.0),
            ("Resource Exhaustion", 0.70, 20, 1.1)
        ],
        "Evacuation Congestion": [
            ("Traffic Collapse", 0.90, 10, 1.5),
        ],
        "Ambulance Delay": [
            ("Hospital Overload", 0.80, 25, 1.3),
        ],
        "Power Outage": [
            ("Traffic Collapse", 0.75, 5, 1.4), # Signals go down
            ("Hospital Overload", 0.50, 45, 1.2) # Backup generators fail
        ]
    }

    def __init__(self):
        pass

    def predict_cascades(self, current_state: GlobalStateModel, current_time: datetime) -> List[PredictedConsequence]:
        """
        Evaluates the current active incidents state, maps them onto the dependency graph,
        and generates a timeline of evolving predicted consequences.
        Supports simultaneous cascading incidents.
        """
        predictions: List[PredictedConsequence] = []
        
        # We track nodes we've evaluated to avoid infinite loops in the graph, 
        # but store accumulating stress per entity.
        evaluated_paths = set()
        
        for inc_id, incident in current_state.active_incidents.items():
            if incident.status in ["Resolved", "Retracted"]:
                continue
                
            # Base entry into the generic graph
            self._traverse_graph(
                current_node=incident.type,
                current_prob=incident.confidence_score,
                current_sev=incident.severity,
                current_time=current_time,
                target_loc=incident.location,
                state=current_state,
                predictions_out=predictions,
                evaluated=evaluated_paths,
                depth=0
            )

        # Merge overlapping predictions for the same target and type (simultaneous cascading amplification)
        merged_predictions = self._merge_and_amplify_predictions(predictions)
        
        # Sort by earliest impact
        merged_predictions.sort(key=lambda p: p.estimated_time)
        return merged_predictions

    def _traverse_graph(
        self, current_node: str, current_prob: float, current_sev: float, 
        current_time: datetime, target_loc: str, state: GlobalStateModel,
        predictions_out: List[PredictedConsequence], evaluated: set, depth: int
    ):
        if depth > 4 or current_prob < 0.2: # Max depth or low probability cutoff
            return
            
        key = (current_node, target_loc)
        if key in evaluated:
            return
        evaluated.add(key)

        edges = self.DEPENDENCY_GRAPH.get(current_node, [])
        
        # Also inject dynamic bridging from state context (e.g., if target is a district)
        district = state.districts.get(target_loc)
        
        for next_node, base_prob, delay_mins, sev_mult in edges:
            # Modify probability based on district vulnerability
            modified_prob = base_prob * (1.0 + (district.vulnerability_index if district else 0.0))
            path_prob = current_prob * min(0.99, modified_prob)
            
            if path_prob >= 0.3: # Threshold to log a prediction
                impact_time = current_time + timedelta(minutes=delay_mins)
                new_sev = min(1.0, current_sev * sev_mult)
                
                # Calculate uncertainty ranges (widens as probability drops and depth increases)
                uncertainty_variance = 0.05 + (depth * 0.05) + ((1.0 - path_prob) * 0.1)
                lower_bound = max(0.0, path_prob - uncertainty_variance)
                upper_bound = min(1.0, path_prob + uncertainty_variance)
                
                target_entity = target_loc
                # Map specific consequences to specific entity IDs (e.g., Hospital Overload targets nearest hospital)
                if next_node == "Hospital Overload" and district:
                    hospitals = [h for h in state.hospitals.values() if h.district_id == district.district_id]
                    if hospitals:
                        target_entity = hospitals[0].hospital_id
                
                pred = PredictedConsequence(
                    consequence_type=next_node,
                    description=f"Predicted {next_node} due to cascading {current_node}",
                    target_entity_id=target_entity,
                    probability=path_prob,
                    uncertainty_range=(lower_bound, upper_bound),
                    estimated_time=impact_time,
                    severity_impact=new_sev
                )
                predictions_out.append(pred)
                
                # Recurse down the cascade chain
                self._traverse_graph(
                    current_node=next_node,
                    current_prob=path_prob,
                    current_sev=new_sev,
                    current_time=impact_time,
                    target_loc=target_loc, # Assuming localized spread for now
                    state=state,
                    predictions_out=predictions_out,
                    evaluated=evaluated.copy(),
                    depth=depth + 1
                )

    def _merge_and_amplify_predictions(self, predictions: List[PredictedConsequence]) -> List[PredictedConsequence]:
        """Combines multiple predictions of the same type/target due to simultaneous crises compounding."""
        merged: Dict[str, PredictedConsequence] = {}
        for p in predictions:
            key = f"{p.target_entity_id}-{p.consequence_type}"
            if key in merged:
                existing = merged[key]
                # Amplify probability using independent probability combination: P(A U B) = P(A) + P(B) - P(A)*P(B)
                amplified_prob = existing.probability + p.probability - (existing.probability * p.probability)
                existing.probability = min(0.99, amplified_prob)
                existing.severity_impact = min(1.0, existing.severity_impact + (p.severity_impact * 0.3))
                # Update time to the earliest occurrence
                existing.estimated_time = min(existing.estimated_time, p.estimated_time)
                # Expand uncertainty bounds
                existing.uncertainty_range = (
                    min(existing.uncertainty_range[0], p.uncertainty_range[0]),
                    max(existing.uncertainty_range[1], p.uncertainty_range[1])
                )
            else:
                merged[key] = p
        return list(merged.values())
