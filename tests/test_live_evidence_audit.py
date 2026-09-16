"""
Tests for Data Provenance Engine & Live Evidence Audit.
Verifies that synthetic data cannot masquerade as live broker execution,
missing broker order IDs are detected as unverified, and genuine records pass.
"""

from src.workstation.models import AuditStatus, EvidenceSource
from src.workstation.provenance import DataProvenanceEngine


def test_audit_valid_live_trade():
    valid_record = {
        "trade_id": "TRD-LIVE-101",
        "strategy": "ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1",
        "symbol": "AMD",
        "broker_order_id": "IBKR-ORD-778811",
        "entry_timestamp": "2026-09-15T09:45:00Z",
        "market_session_date": "2026-09-15",
        "evidence_source": EvidenceSource.BROKER_LIVE,
    }
    status, msg = DataProvenanceEngine.validate_live_trade_record(valid_record)
    assert status == AuditStatus.VERIFIED_LIVE
    assert "verified against broker ledger" in msg


def test_audit_synthetic_trade_labeled_live_fails():
    synthetic_record = {
        "trade_id": "TRD-MOCK-SYNTHETIC-99",
        "strategy": "ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1",
        "symbol": "AMD",
        "broker_order_id": "SYNTHETIC-ORDER-001",
        "entry_timestamp": "2026-09-15T09:45:00Z",
        "market_session_date": "2026-09-15",
        "evidence_source": EvidenceSource.BROKER_LIVE,
    }
    status, msg = DataProvenanceEngine.validate_live_trade_record(synthetic_record)
    assert status == AuditStatus.INVALID_LIVE_LABEL
    assert "synthetic markers" in msg


def test_audit_live_trade_missing_broker_id_fails():
    unverified_record = {
        "trade_id": "TRD-LIVE-102",
        "strategy": "ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        "symbol": "AAPL",
        "broker_order_id": "",  # Missing broker ID
        "entry_timestamp": "2026-09-15T09:30:00Z",
        "market_session_date": "2026-09-15",
        "evidence_source": EvidenceSource.BROKER_LIVE,
    }
    status, msg = DataProvenanceEngine.validate_live_trade_record(unverified_record)
    assert status == AuditStatus.UNVERIFIED_LIVE
    assert "lacks a valid broker_order_id" in msg


def test_audit_batch_ledger_summary():
    records = [
        {
            "trade_id": "TRD-1",
            "strategy": "ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1",
            "symbol": "AMD",
            "broker_order_id": "IBKR-1",
            "entry_timestamp": "2026-09-15T09:45:00Z",
            "evidence_source": EvidenceSource.BROKER_LIVE,
        },
        {
            "trade_id": "TRD-2",
            "strategy": "ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
            "symbol": "TSLA",
            "broker_order_id": "IBKR-2",
            "entry_timestamp": "2026-09-15T09:30:00Z",
            "evidence_source": EvidenceSource.BROKER_LIVE,
        },
    ]
    summary = DataProvenanceEngine.audit_live_evidence(records)
    assert summary.total_records_inspected == 2
    assert summary.verified_live_count == 2
    assert summary.overall_status == AuditStatus.VERIFIED_LIVE
