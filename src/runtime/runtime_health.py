"""
Runtime Health & Heartbeat Services (Phase F).

Monitors data freshness, broker connection health, event service status,
and emits periodic runtime heartbeats.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, timezone


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RuntimeHeartbeat:
    timestamp: str
    session_id: str
    runtime_state: str
    health_status: HealthStatus
    active_positions_count: int
    data_freshness_seconds: float
    unhealthy_components: List[str]


class RuntimeHealthMonitor:
    """
    Monitors operational health of all integrated sub-services.
    """
    def __init__(self, max_stale_seconds: float = 300.0):
        self.max_stale_seconds = max_stale_seconds

    def check_health(
        self,
        is_broker_connected: bool = True,
        is_market_data_fresh: bool = True,
        is_event_service_healthy: bool = True,
        data_freshness_seconds: float = 5.0,
    ) -> HealthStatus:
        if not is_broker_connected or not is_market_data_fresh:
            return HealthStatus.CRITICAL
        if not is_event_service_healthy or data_freshness_seconds > self.max_stale_seconds:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY
