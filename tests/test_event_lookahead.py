"""
Tests for Point-in-Time Event Lookahead and Publication Leakage Firewalls.
"""

import pytest
from src.events.event_types import EventFamily, EventSeverity, EventRecord, PolicyAction
from src.events.event_cache import PointInTimeEventCache
from src.events.event_risk_policy import EventRiskPolicy


def test_future_event_not_visible_before_publication():
    cache = PointInTimeEventCache()
    # Breaking news published at 14:00:00Z
    ev = EventRecord(
        event_id="DOJ_GOOG_20250115",
        symbol="GOOGL",
        event_type=EventFamily.MAJOR_LEGAL_GOVERNMENT,
        event_subtype="DOJ_ANTITRUST_RULING",
        source="DOJ_PRESS",
        source_timestamp="2025-01-15T14:00:00Z",
        effective_timestamp="2025-01-15T14:00:00Z",
        expiry_timestamp="2025-01-16T16:00:00Z",
        severity=EventSeverity.CRITICAL,
        confidence=1.0,
    )
    cache.add_event(ev)
    policy = EventRiskPolicy(event_cache=cache)

    # 1. Query at 10:00:00Z (before publication) -> Must NOT see event (ALLOW)
    dec_morning = policy.evaluate(symbol="GOOGL", timestamp="2025-01-15T10:00:00Z")
    assert dec_morning.action == PolicyAction.ALLOW
    assert not dec_morning.is_vetoed
    assert policy.audit_tracker.total_lookahead_violations == 0

    # 2. Query at 14:05:00Z (after publication) -> Must see event (VETO)
    dec_afternoon = policy.evaluate(symbol="GOOGL", timestamp="2025-01-15T14:05:00Z")
    assert dec_afternoon.action == PolicyAction.VETO
    assert dec_afternoon.is_vetoed
    assert policy.audit_tracker.total_lookahead_violations == 0


def test_audit_tracker_flags_lookahead_tampering():
    cache = PointInTimeEventCache()
    policy = EventRiskPolicy(event_cache=cache)

    # Fabricate an invalid lookahead condition manually to ensure tracker catches it
    future_ev = EventRecord(
        event_id="LEAKED_EVENT",
        symbol="TSLA",
        event_type=EventFamily.REGULATORY_DECISION,
        event_subtype="SEC_SUBPOENA",
        source="SEC",
        source_timestamp="2025-01-15T18:00:00Z",
        effective_timestamp="2025-01-15T18:00:00Z",
        expiry_timestamp="2025-01-16T18:00:00Z",
        severity=EventSeverity.HIGH,
        confidence=1.0,
    )
    # Directly evaluate with injected future event
    entry = policy.audit_tracker.record_decision(
        decision=policy.evaluate("TSLA", "2025-01-15T10:00:00Z"),
        active_events=[future_ev],
    )
    assert not entry.lookahead_clean
    assert policy.audit_tracker.total_lookahead_violations == 1
