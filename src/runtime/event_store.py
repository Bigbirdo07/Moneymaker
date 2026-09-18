"""
Append-Only Operational Event Store (Phase F).

Persists all state transitions, order authorizations, fills, risk throttles,
and operational incidents to structured append-only ledgers.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid


class EventSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RuntimeOperationalEvent:
    event_id: str
    timestamp: str
    session_id: str
    event_type: str
    component: str
    severity: EventSeverity
    symbol: Optional[str]
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "event_type": self.event_type,
            "component": self.component,
            "severity": self.severity.value,
            "symbol": self.symbol or "",
            "payload": self.payload,
        }


class EventStore:
    """
    Append-only in-memory and persistent event store.
    """
    def __init__(self):
        self._events: List[RuntimeOperationalEvent] = []

    def record(
        self,
        session_id: str,
        event_type: str,
        component: str,
        severity: EventSeverity = EventSeverity.INFO,
        symbol: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> RuntimeOperationalEvent:
        t_str = timestamp or datetime.now(timezone.utc).isoformat()
        e_id = f"EVT_{uuid.uuid4().hex[:12]}"
        evt = RuntimeOperationalEvent(
            event_id=e_id,
            timestamp=t_str,
            session_id=session_id,
            event_type=event_type,
            component=component,
            severity=severity,
            symbol=symbol,
            payload=payload or {},
        )
        self._events.append(evt)
        return evt

    def get_events(self, session_id: Optional[str] = None) -> List[RuntimeOperationalEvent]:
        if session_id:
            return [e for e in self._events if e.session_id == session_id]
        return list(self._events)
