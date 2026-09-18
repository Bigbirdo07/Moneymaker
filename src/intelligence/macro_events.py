"""
Macroeconomic Event Provider & Policy Engine (Phase E).

Tracks scheduled economic calendar releases (CPI, PPI, FOMC, Jobs Report)
and evaluates whether market-wide caution or entry suspensions are required.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime


class MacroImportance(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class MacroEvent:
    event_id: str
    event_name: str
    scheduled_timestamp: str  # ISO-8601
    importance: str           # "HIGH", "MEDIUM", "LOW"
    source: str
    description: str


class MacroEventProvider:
    """
    Ingests scheduled point-in-time macroeconomic releases.
    """
    def __init__(self, events: Optional[List[MacroEvent]] = None):
        self._events = events or []

    def get_events_for_date(self, date_str: str) -> List[MacroEvent]:
        return [e for e in self._events if e.scheduled_timestamp.startswith(date_str)]

    def is_macro_release_imminent(self, current_timestamp: str, buffer_minutes: int = 15) -> bool:
        """
        Returns True if a high-importance macro release is scheduled within buffer_minutes.
        """
        for e in self._events:
            if e.importance == "HIGH" or e.importance == MacroImportance.HIGH.value:
                # Check if current timestamp is within buffer window before or after release
                if e.scheduled_timestamp.startswith(current_timestamp[:10]):
                    curr_t = current_timestamp[11:19]
                    sched_t = e.scheduled_timestamp[11:19]
                    if abs(self._time_to_minutes(curr_t) - self._time_to_minutes(sched_t)) <= buffer_minutes:
                        return True
        return False

    def _time_to_minutes(self, t_str: str) -> int:
        parts = t_str.split(":")
        if len(parts) >= 2:
            return int(parts[0]) * 60 + int(parts[1])
        return 0


class MacroEventPolicy:
    """
    Evaluates whether active or imminent macro releases require risk throttling.
    """
    def __init__(self, provider: Optional[MacroEventProvider] = None):
        self.provider = provider or MacroEventProvider()

    def evaluate_macro_risk(self, timestamp: str) -> Dict[str, Any]:
        imminent = self.provider.is_macro_release_imminent(timestamp, buffer_minutes=15)
        return {
            "macro_risk_active": imminent,
            "recommended_multiplier": 0.5 if imminent else 1.0,
            "policy_action": "SUSPEND_NEW_ENTRIES" if imminent else "ALLOW_NORMAL_DEPLOYMENT",
        }
