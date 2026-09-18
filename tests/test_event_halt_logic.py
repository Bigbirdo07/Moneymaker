"""
Tests for Trading Halt logic and trapped position handling.
"""

import pytest
from src.events.event_types import (
    EventFamily,
    EventSeverity,
    EventRecord,
    PolicyAction,
    OpenPositionAction,
)
from src.events.event_cache import PointInTimeEventCache
from src.events.event_risk_policy import EventRiskPolicy


def test_trading_halt_prohibits_new_entry():
    cache = PointInTimeEventCache()
    ev = EventRecord(
        event_id="HALT_TSLA_20250115_101500",
        symbol="TSLA",
        event_type=EventFamily.TRADING_HALT,
        event_subtype="LULD_PAUSE",
        source="NASDAQ_HALTS",
        source_timestamp="2025-01-15T10:15:00Z",
        effective_timestamp="2025-01-15T10:15:00Z",
        expiry_timestamp="2025-01-15T10:20:00Z",
        severity=EventSeverity.CRITICAL,
        confidence=1.0,
    )
    cache.add_event(ev)
    policy = EventRiskPolicy(event_cache=cache)

    # During halt -> VETO new entry, Open Position is FREEZE_NO_ACTION_IF_HALTED
    dec = policy.evaluate("TSLA", "2025-01-15T10:16:00Z", has_open_position=True)
    assert dec.action == PolicyAction.VETO
    assert dec.open_position_action == OpenPositionAction.FREEZE_NO_ACTION_IF_HALTED
    assert "TRADING_HALT_LULD_PAUSE" in dec.reason_codes[0]


def test_trading_halt_resumption_restores_tradability():
    cache = PointInTimeEventCache()
    ev = EventRecord(
        event_id="HALT_TSLA_20250115_101500",
        symbol="TSLA",
        event_type=EventFamily.TRADING_HALT,
        event_subtype="LULD_PAUSE",
        source="NASDAQ_HALTS",
        source_timestamp="2025-01-15T10:15:00Z",
        effective_timestamp="2025-01-15T10:15:00Z",
        expiry_timestamp="2025-01-15T10:20:00Z",
        severity=EventSeverity.CRITICAL,
        confidence=1.0,
    )
    cache.add_event(ev)
    policy = EventRiskPolicy(event_cache=cache)

    # After halt expires at 10:20:00Z -> ALLOW
    dec = policy.evaluate("TSLA", "2025-01-15T10:21:00Z")
    assert dec.action == PolicyAction.ALLOW
    assert not dec.is_vetoed
