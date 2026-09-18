"""
Unit tests for deterministic EventRiskPolicy rule evaluation.
"""

import pytest
from src.events.event_types import (
    EventFamily,
    PolicyAction,
    OpenPositionAction,
    EventSeverity,
    EventRecord,
)
from src.events.event_cache import PointInTimeEventCache
from src.events.event_risk_policy import EventRiskPolicy


def test_clean_symbol_returns_allow():
    cache = PointInTimeEventCache()
    policy = EventRiskPolicy(event_cache=cache)

    decision = policy.evaluate(symbol="AAPL", timestamp="2025-01-15T10:00:00Z")
    assert decision.action == PolicyAction.ALLOW
    assert decision.open_position_action == OpenPositionAction.HOLD
    assert decision.size_multiplier == 1.0
    assert not decision.is_vetoed
    assert decision.is_permitted


def test_same_day_earnings_triggers_veto():
    cache = PointInTimeEventCache()
    ev = EventRecord(
        event_id="EARN_NVDA_20250115",
        symbol="NVDA",
        event_type=EventFamily.EARNINGS,
        event_subtype="AFTER_CLOSE",
        source="TEST_FEED",
        source_timestamp="2025-01-15T00:00:00Z",
        effective_timestamp="2025-01-15T16:00:00Z",
        expiry_timestamp="2025-01-16T09:30:00Z",
        severity=EventSeverity.HIGH,
        confidence=0.99,
        known_before_open=True,
    )
    cache.add_event(ev)
    policy = EventRiskPolicy(event_cache=cache)

    decision = policy.evaluate(symbol="NVDA", timestamp="2025-01-15T10:30:00Z")
    assert decision.action == PolicyAction.VETO
    assert decision.is_vetoed
    assert not decision.is_permitted
    assert "EARNINGS_ANNOUNCEMENT_AFTER_CLOSE" in decision.reason_codes[0]


def test_dilution_offering_triggers_reduce_risk():
    cache = PointInTimeEventCache()
    ev = EventRecord(
        event_id="OFFER_PLTR_20250115",
        symbol="PLTR",
        event_type=EventFamily.SHARE_OFFERING_DILUTION,
        event_subtype="SECONDARY_OFFERING",
        source="SEC_EDGAR",
        source_timestamp="2025-01-15T06:00:00Z",
        effective_timestamp="2025-01-15T09:30:00Z",
        expiry_timestamp="2025-01-15T16:00:00Z",
        severity=EventSeverity.MEDIUM,
        confidence=0.95,
        known_before_open=True,
    )
    cache.add_event(ev)
    policy = EventRiskPolicy(event_cache=cache)

    decision = policy.evaluate(symbol="PLTR", timestamp="2025-01-15T10:00:00Z")
    assert decision.action == PolicyAction.REDUCE_RISK
    assert decision.size_multiplier == 0.50
    assert decision.is_permitted
    assert not decision.is_vetoed


def test_fda_binary_event_triggers_veto_and_exit():
    cache = PointInTimeEventCache()
    ev = EventRecord(
        event_id="FDA_BIIB_20250115",
        symbol="BIIB",
        event_type=EventFamily.CLINICAL_FDA_BINARY,
        event_subtype="PDUFA_DATE",
        source="FDA_CALENDAR",
        source_timestamp="2025-01-15T00:00:00Z",
        effective_timestamp="2025-01-15T09:30:00Z",
        expiry_timestamp="2025-01-15T20:00:00Z",
        severity=EventSeverity.CRITICAL,
        confidence=1.0,
        known_before_open=True,
    )
    cache.add_event(ev)
    policy = EventRiskPolicy(event_cache=cache)

    decision = policy.evaluate(symbol="BIIB", timestamp="2025-01-15T11:00:00Z", has_open_position=True)
    assert decision.action == PolicyAction.VETO
    assert decision.open_position_action == OpenPositionAction.EXIT
    assert decision.is_vetoed
