"""Tests for SystemReadinessMonitor & Stale Data (Phases E27, E28)."""

import pytest
from src.intelligence.system_readiness import (
    SystemReadinessMonitor,
    ReadinessState,
)


def test_system_readiness_all_ok():
    monitor = SystemReadinessMonitor(max_allowed_staleness_seconds=300.0)
    report = monitor.evaluate_readiness(
        last_market_data_timestamp="2026-09-18T08:44:45Z",
        current_timestamp="2026-09-18T08:45:00Z",
        event_service_healthy=True,
        universe_service_healthy=True,
    )
    assert report.state == ReadinessState.READY
    assert report.is_ready_for_session
    assert len(report.unhealthy_services) == 0


def test_system_readiness_unhealthy_event_service():
    monitor = SystemReadinessMonitor(max_allowed_staleness_seconds=300.0)
    report = monitor.evaluate_readiness(
        last_market_data_timestamp="2026-09-18T08:44:45Z",
        current_timestamp="2026-09-18T08:45:00Z",
        event_service_healthy=False,
        universe_service_healthy=True,
    )
    assert report.state == ReadinessState.DEGRADED
    assert "EVENT_RISK_SERVICE" in report.unhealthy_services
