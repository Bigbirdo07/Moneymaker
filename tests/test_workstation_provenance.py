"""
Tests for Workstation Evidence Badges & Data Availability Invariants.
Verifies that unknown or unmonitored tickers return DATA UNAVAILABLE rather than
invented synthetic prices, and all telemetry carries evidence source badges.
"""

from src.workstation.models import EvidenceSource
from src.workstation.service import WorkstationService


def test_data_unavailable_for_unknown_symbol():
    service = WorkstationService()
    quote = service.get_live_quote("NON_EXISTENT_TICKER")
    assert quote.is_data_available is False
    assert quote.last_price == 0.0


def test_data_available_for_monitored_symbol():
    service = WorkstationService()
    quote = service.get_live_quote("NVDA")
    assert quote.is_data_available is True
    assert quote.last_price > 0.0


def test_evidence_badges_present_on_all_core_models():
    service = WorkstationService()
    acc = service.get_account_summary()
    assert acc.evidence_source == EvidenceSource.BROKER_LIVE

    strats = service.get_strategy_cards()
    for s in strats:
        assert s.evidence_source == EvidenceSource.BROKER_LIVE

    positions = service.get_positions()
    for p in positions:
        assert p.evidence_source == EvidenceSource.BROKER_LIVE

    trades = service.get_trades()
    for t in trades:
        assert t.evidence_source == EvidenceSource.BROKER_LIVE
