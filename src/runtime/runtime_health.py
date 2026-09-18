"""
Runtime Health, Heartbeat & Stay-Awake Services (Phase F).

Monitors data freshness, broker connection health, event service status,
emits periodic runtime heartbeats, and prevents OS sleep during active trading sessions.
"""

from dataclasses import dataclass, field
from enum import Enum
import logging
import os
import platform
import subprocess
import sys
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger("src.runtime.runtime_health")


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


class StayAwakeGuard:
    """
    Context manager preventing OS sleep/hibernation during active trading sessions.
    On macOS (Darwin), utilizes `caffeinate` bound to process lifecycle.
    """
    def __init__(self, description: str = "Moneymaker Active Session"):
        self.description = description
        self._proc: Optional[subprocess.Popen] = None
        self.is_active = False

    def __enter__(self) -> "StayAwakeGuard":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    def start(self) -> bool:
        if self.is_active:
            return True
        if sys.platform == "darwin":
            try:
                # Prevent system and display sleep while current PID is running
                self._proc = subprocess.Popen(
                    ["caffeinate", "-i", "-s", "-w", str(os.getpid())],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self.is_active = True
                logger.info("StayAwakeGuard activated (macOS caffeinate PID: %s).", self._proc.pid)
                return True
            except Exception as e:
                logger.warning("Failed to spawn caffeinate stay-awake guard: %s", e)
                return False
        else:
            logger.info("StayAwakeGuard active on non-macOS platform (%s).", sys.platform)
            self.is_active = True
            return True

    def stop(self) -> None:
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=2.0)
                logger.info("StayAwakeGuard deactivated cleanly.")
            except Exception as e:
                logger.warning("Error stopping caffeinate process: %s", e)
        self.is_active = False


class RuntimeHealthMonitor:
    """
    Monitors operational health of all integrated sub-services.
    """
    def __init__(self, max_stale_seconds: float = 300.0):
        self.max_stale_seconds = max_stale_seconds
        self.heartbeat_history: List[RuntimeHeartbeat] = []
        self.last_heartbeat_time: float = time.time()

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

    def emit_heartbeat(
        self,
        session_id: str,
        runtime_state: str,
        active_positions_count: int,
        data_freshness_seconds: float = 1.0,
        is_broker_connected: bool = True,
        is_market_data_fresh: bool = True,
        is_event_service_healthy: bool = True,
    ) -> RuntimeHeartbeat:
        unhealthy = []
        if not is_broker_connected:
            unhealthy.append("BROKER_DISCONNECTED")
        if not is_market_data_fresh or data_freshness_seconds > self.max_stale_seconds:
            unhealthy.append("MARKET_DATA_STALE")
        if not is_event_service_healthy:
            unhealthy.append("EVENT_SERVICE_UNHEALTHY")

        status = self.check_health(
            is_broker_connected=is_broker_connected,
            is_market_data_fresh=is_market_data_fresh,
            is_event_service_healthy=is_event_service_healthy,
            data_freshness_seconds=data_freshness_seconds,
        )

        hb = RuntimeHeartbeat(
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=session_id,
            runtime_state=runtime_state,
            health_status=status,
            active_positions_count=active_positions_count,
            data_freshness_seconds=data_freshness_seconds,
            unhealthy_components=unhealthy,
        )
        self.heartbeat_history.append(hb)
        self.last_heartbeat_time = time.time()
        return hb

