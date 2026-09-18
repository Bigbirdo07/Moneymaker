"""
Tests for event expiration, cooldown, and stabilization lifecycles.
"""

import pytest
from src.events.event_types import EventFamily, EventSeverity, EventRecord, PolicyAction
from src.events.event_cache import PointInTimeEventCache
from src.events.event_risk_policy import EventRiskPolicy


def test_event_expires_properly():
    cache = PointInTimeEventCache()
    # Earnings event active on 2025-01-15 until market close 16:00:00Z
    ev = EventRecord(
        event_id="EARN_NFLX_20250115",
        symbol="NFLX",
        event_type=EventFamily.EARNINGS,
        event_subtype="BEFORE_OPEN",
        source="FEED",
        source_timestamp="2025-01-15T00:00:00Z",
        effective_timestamp="2025-01-15T09:30:00Z",
        expiry_timestamp="2025-01-15T16:00:00Z",
        severity=EventSeverity.HIGH,
        confidence=1.0,
    )
    cache.add_event(ev)
    policy = EventRiskPolicy(event_cache=cache)

    # Active during trading hours on event day
    dec_active = policy.evaluate("NFLX", "2025-01-15T11:00:00Z")
    assert dec_active.action == PolicyAction.VETO

    # Expired the following morning
    dec_next_day = policy.evaluate("NFLX", "2025-01-16T09:35:00Z")
    assert dec_next_day.action == PolicyAction.ALLOW
    assert not dec_next_day.is_vetoed
