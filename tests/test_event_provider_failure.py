"""
Tests for event provider degradation, service failure, and fail-safe handling.
"""

import pytest
from src.events.event_types import PolicyAction
from src.events.event_service_health import (
    EventServiceHealthManager,
    EventServiceHealthState,
    FailSafeMode,
)
from src.events.event_risk_policy import EventRiskPolicy


def test_provider_consecutive_failures_trigger_fail_safe():
    health = EventServiceHealthManager(fail_safe_mode=FailSafeMode.STRICT_VETO)
    health.register_provider("NASDAQ_HALTS")

    # Record 3 failures
    health.record_failure("NASDAQ_HALTS", "Connection timeout")
    health.record_failure("NASDAQ_HALTS", "HTTP 503")
    assert health.overall_health_state == EventServiceHealthState.DEGRADED

    health.record_failure("NASDAQ_HALTS", "Feed down")
    assert health.overall_health_state == EventServiceHealthState.UNAVAILABLE

    policy = EventRiskPolicy(health_manager=health)
    dec = policy.evaluate("AAPL", "2025-01-15T10:00:00Z")

    # Strict veto mode prohibits trading during provider outage
    assert dec.action == PolicyAction.VETO
    assert dec.is_vetoed
    assert "SERVICE_HEALTH_EVENT_SERVICE_UNAVAILABLE" in dec.reason_codes[0]


def test_provider_recovery_restores_healthy_state():
    health = EventServiceHealthManager(fail_safe_mode=FailSafeMode.STRICT_VETO)
    health.register_provider("NASDAQ_HALTS")
    health.record_failure("NASDAQ_HALTS", "Temporary network drop")
    assert health.overall_health_state == EventServiceHealthState.DEGRADED

    health.record_heartbeat("NASDAQ_HALTS")
    assert health.overall_health_state == EventServiceHealthState.HEALTHY

    policy = EventRiskPolicy(health_manager=health)
    dec = policy.evaluate("AAPL", "2025-01-15T10:00:00Z")
    assert dec.action == PolicyAction.ALLOW
