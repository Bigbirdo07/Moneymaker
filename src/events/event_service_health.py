"""
Event Service Health Monitoring & Fail-Safe Handler.

Tracks upstream event provider statuses and enforces deterministic fail-safe behavior
(e.g., degraded or unavailable feeds trigger REDUCE_RISK or VETO rather than assuming clean state).
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone

from src.events.event_types import PolicyAction


class EventServiceHealthState(str, Enum):
    HEALTHY = "EVENT_SERVICE_HEALTHY"
    DEGRADED = "EVENT_SERVICE_DEGRADED"
    UNAVAILABLE = "EVENT_SERVICE_UNAVAILABLE"


class FailSafeMode(str, Enum):
    STRICT_VETO = "STRICT_VETO"             # Prohibit all new entries if any critical feed fails
    REDUCE_RISK = "REDUCE_RISK"             # Allow trading with 50% size reduction and warning
    ALLOW_WITH_WARN = "ALLOW_WITH_WARN"     # Research-only fail-open mode


@dataclass
class ProviderHealthStatus:
    provider_name: str
    state: EventServiceHealthState
    last_heartbeat: str
    error_count: int = 0
    consecutive_failures: int = 0
    last_error_message: Optional[str] = None


class EventServiceHealthManager:
    """
    Manages and assesses the health of all attached event providers.
    """
    def __init__(self, fail_safe_mode: FailSafeMode = FailSafeMode.STRICT_VETO):
        self.fail_safe_mode = fail_safe_mode
        self._provider_health: Dict[str, ProviderHealthStatus] = {}

    def register_provider(self, provider_name: str) -> None:
        self._provider_health[provider_name] = ProviderHealthStatus(
            provider_name=provider_name,
            state=EventServiceHealthState.HEALTHY,
            last_heartbeat=datetime.now(timezone.utc).isoformat() + "Z",
        )

    def record_heartbeat(self, provider_name: str) -> None:
        if provider_name in self._provider_health:
            stat = self._provider_health[provider_name]
            stat.last_heartbeat = datetime.now(timezone.utc).isoformat() + "Z"
            stat.consecutive_failures = 0
            stat.state = EventServiceHealthState.HEALTHY

    def record_failure(self, provider_name: str, error_msg: str) -> None:
        if provider_name not in self._provider_health:
            self.register_provider(provider_name)
        stat = self._provider_health[provider_name]
        stat.error_count += 1
        stat.consecutive_failures += 1
        stat.last_error_message = error_msg
        if stat.consecutive_failures >= 3:
            stat.state = EventServiceHealthState.UNAVAILABLE
        else:
            stat.state = EventServiceHealthState.DEGRADED

    @property
    def overall_health_state(self) -> EventServiceHealthState:
        if not self._provider_health:
            return EventServiceHealthState.HEALTHY
        states = [p.state for p in self._provider_health.values()]
        if any(s == EventServiceHealthState.UNAVAILABLE for s in states):
            return EventServiceHealthState.UNAVAILABLE
        if any(s == EventServiceHealthState.DEGRADED for s in states):
            return EventServiceHealthState.DEGRADED
        return EventServiceHealthState.HEALTHY

    def get_fail_safe_action(self) -> Optional[PolicyAction]:
        """
        Determines if a global fail-safe action must be triggered due to feed health.
        """
        overall = self.overall_health_state
        if overall == EventServiceHealthState.HEALTHY:
            return None
        if overall == EventServiceHealthState.UNAVAILABLE:
            if self.fail_safe_mode == FailSafeMode.STRICT_VETO:
                return PolicyAction.VETO
            elif self.fail_safe_mode == FailSafeMode.REDUCE_RISK:
                return PolicyAction.REDUCE_RISK
            return PolicyAction.WARN
        if overall == EventServiceHealthState.DEGRADED:
            if self.fail_safe_mode == FailSafeMode.STRICT_VETO:
                return PolicyAction.REDUCE_RISK
            return PolicyAction.WARN
        return None
