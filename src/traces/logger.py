from pydantic import BaseModel
from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import logging

class TraceRecord(BaseModel):
    """Structured record for an agent's reasoning or action log."""
    trace_id: str
    timestamp: datetime = datetime.utcnow()
    agent_name: str
    action_type: str
    trigger_event_id: Optional[str] = None
    reasoning: str
    confidence_score: float
    trade_offs_considered: List[str] = []
    metadata: Dict[str, Any] = {}

class TraceLogger:
    """
    Centralized observability logger for the Multi-Agent System.
    Stores traces in-memory for the session (and logs them structurally to stdout).
    Later, this can export to Elasticsearch, Datadog, or OpenTelemetry.
    """
    def __init__(self):
        self._traces: List[TraceRecord] = []
        self._logger = logging.getLogger("system.traces")
        # Ensure we can distinctively log these
        self._logger.setLevel(logging.INFO)

    def log_decision(
        self,
        trace_id: str,
        agent_name: str,
        action_type: str,
        reasoning: str,
        confidence_score: float,
        trigger_event_id: Optional[str] = None,
        trade_offs: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Log an agent's decision and reasoning."""
        record = TraceRecord(
            trace_id=trace_id,
            agent_name=agent_name,
            action_type=action_type,
            trigger_event_id=trigger_event_id,
            reasoning=reasoning,
            confidence_score=confidence_score,
            trade_offs_considered=trade_offs or [],
            metadata=metadata or {}
        )
        self._traces.append(record)
        
        # Output as JSON string for easy log aggregation parsing
        log_payload = record.model_dump_json()
        self._logger.info(f"AGENT_TRACE: {log_payload}")

    def get_traces_for_agent(self, agent_name: str) -> List[TraceRecord]:
        """Retrieve historical traces for a specific agent."""
        return [t for t in self._traces if t.agent_name == agent_name]

    def get_traces_by_event(self, event_id: str) -> List[TraceRecord]:
        """Retrieve all agent decisions triggered by a specific event."""
        return [t for t in self._traces if t.trigger_event_id == event_id]
        
    def get_all_traces(self) -> List[TraceRecord]:
        return self._traces

    def get_operational_outcomes(self) -> List[TraceRecord]:
        """Traces that represent a final agent decision (not intermediate reasoning)."""
        return [
            t
            for t in self._traces
            if t.action_type == "OperationalOutcome"
            or (t.metadata or {}).get("display_kind") == "outcome"
        ]
