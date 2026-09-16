"""
Tests for Grounded Trade Explanations.
Verifies that trade explanations contain STRATEGY, SIGNAL, WHY SELECTED,
EXPECTED EDGE, RISK CHECKS, EXECUTION, and CURRENT/FINAL RESULT without fabrication.
"""

from src.workstation.service import WorkstationService


def test_trade_explanation_alpha_a():
    service = WorkstationService()
    exp = service.explain_trade("TRD-20260915-001")
    assert exp.trade_id == "TRD-20260915-001"
    assert exp.symbol == "AMD"
    assert "ALPHA_A" in exp.strategy
    assert "Relative Momentum" in exp.signal_summary
    assert "surged" in exp.why_selected or "VWAP" in exp.why_selected
    assert "+1.11 bps net edge" in exp.expected_edge
    assert len(exp.risk_checks) >= 3
    assert "Limit order" in exp.execution_details
    assert "Realized PnL" in exp.current_result


def test_trade_explanation_alpha_b():
    service = WorkstationService()
    exp = service.explain_trade("TRD-20260915-002")
    assert exp.trade_id == "TRD-20260915-002"
    assert exp.symbol == "TSLA"
    assert "ALPHA_B" in exp.strategy
    assert "Reversal" in exp.signal_summary
    assert "+10.40 bps net edge" in exp.expected_edge
    assert len(exp.risk_checks) >= 3
    assert "Market-On-Open" in exp.execution_details


def test_trade_explanation_unknown_trade():
    service = WorkstationService()
    exp = service.explain_trade("TRD-NONEXISTENT")
    assert exp.symbol == "UNKNOWN"
    assert "not found" in exp.signal_summary
