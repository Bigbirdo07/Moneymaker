"""
Unit & Integration Tests for Alpha B Governed Live Micro Mode (Phase 7B Track B).
Validates human approval workflows, expiry cutoffs, short order fatal rejection,
capital firewall ($1,000 max), overnight gap gate, corporate event veto,
same-symbol stacking cap, kill switches, and triple-book matching.
"""

import pytest
import pandas as pd

from src.broker.adapter import ExecutionMode
from src.strategies.alpha_b_reversal import (
    AlphaBExecutionViolation,
    AlphaBLiveGovernedEngine,
    AlphaBLiveApprovalStatus,
    AlphaBRejectionReasonCode,
)


def test_alpha_b_live_governed_mode_permissions_and_capital_firewall():
    """Verifies Alpha B permits ALPHA_B_LIVE_GOVERNED_MICRO with max $1,000 capital and blocks generic live."""
    engine = AlphaBLiveGovernedEngine(
        execution_mode=ExecutionMode.ALPHA_B_LIVE_GOVERNED_MICRO,
        authorized_capital_usd=1000.0,
    )
    assert engine.execution_mode == ExecutionMode.ALPHA_B_LIVE_GOVERNED_MICRO
    assert engine.authorized_capital_usd == 1000.0

    # Test capital cannot exceed $1,000
    engine_overcap = AlphaBLiveGovernedEngine(
        execution_mode=ExecutionMode.ALPHA_B_LIVE_GOVERNED_MICRO,
        authorized_capital_usd=5000.0,
    )
    assert engine_overcap.authorized_capital_usd == 1000.0

    # Test generic live modes are fatal blocked
    for blocked_mode in (
        ExecutionMode.LIVE,
        ExecutionMode.LIVE_AUTONOMOUS_MICRO,
        ExecutionMode.LIVE_GOVERNED_MICRO,
    ):
        with pytest.raises(AlphaBExecutionViolation):
            AlphaBLiveGovernedEngine(execution_mode=blocked_mode)


def test_alpha_b_long_only_enforcement_and_short_fatal_rejection():
    """Verifies that short sell orders are strictly fatal rejected."""
    engine = AlphaBLiveGovernedEngine()
    assert engine.validate_long_only_order("BUY") is True
    assert engine.validate_long_only_order("buy") is True

    with pytest.raises(AlphaBExecutionViolation, match="Long-Only"):
        engine.validate_long_only_order("SELL")


def test_two_stage_human_approval_workflow_and_expiry():
    """Verifies proposal creation, human approval signature, and expiry handling."""
    engine = AlphaBLiveGovernedEngine()

    # 1. Create proposal post-close
    prop = engine.create_live_proposal(
        proposal_id="PROP_20260915_NVDA",
        decision_date="2026-09-15",
        symbol="NVDA",
        notional_usd=333.33,
        signal_score=0.85,
        created_at="2026-09-15 16:05:00",
        expires_at="2026-09-16 09:15:00",
    )
    assert prop.status == AlphaBLiveApprovalStatus.PENDING

    # 2. Approved on time
    prop_approved = engine.submit_human_approval(
        proposal_id="PROP_20260915_NVDA",
        approver="RISK_OFFICER_001",
        approved=True,
        current_time_str="2026-09-16 08:30:00",
    )
    assert prop_approved.status == AlphaBLiveApprovalStatus.APPROVED
    assert prop_approved.approver == "RISK_OFFICER_001"

    # 3. Create second proposal and test expiration
    prop2 = engine.create_live_proposal(
        proposal_id="PROP_20260915_AMD",
        decision_date="2026-09-15",
        symbol="AMD",
        notional_usd=333.33,
        signal_score=0.78,
        created_at="2026-09-15 16:05:00",
        expires_at="2026-09-16 09:15:00",
    )
    prop_expired = engine.submit_human_approval(
        proposal_id="PROP_20260915_AMD",
        approver="RISK_OFFICER_001",
        approved=True,
        current_time_str="2026-09-16 09:20:00", # Past 09:15 ET cutoff
    )
    assert prop_expired.status == AlphaBLiveApprovalStatus.EXPIRED
    assert prop_expired.rejection_reason == AlphaBRejectionReasonCode.STALE_DATA


def test_pre_open_revalidation_gap_gate_and_event_veto():
    """Verifies pre-open revalidation: overnight gap gate (>1.5%) and corporate event veto."""
    engine = AlphaBLiveGovernedEngine()

    # Proposal 1: Normal gap (<1.5%), no event -> PASS
    prop1 = engine.create_live_proposal(
        proposal_id="PROP_NVDA",
        decision_date="2026-09-15",
        symbol="NVDA",
        notional_usd=333.33,
        signal_score=0.85,
        created_at="2026-09-15 16:05:00",
        expires_at="2026-09-16 09:15:00",
    )
    engine.submit_human_approval("PROP_NVDA", "RISK_OFFICER", True, "2026-09-16 08:30:00")
    ok1, msg1 = engine.revalidate_pre_open(
        proposal_id="PROP_NVDA",
        current_premarket_price=121.0,
        prev_close_price=120.0, # +0.83% gap (<1.5%)
        has_corporate_event=False,
    )
    assert ok1 is True
    assert prop1.pre_open_revalidated is True

    # Proposal 2: Extreme gap (2.5% > 1.5%) -> REJECT
    prop2 = engine.create_live_proposal(
        proposal_id="PROP_TSLA",
        decision_date="2026-09-15",
        symbol="TSLA",
        notional_usd=333.33,
        signal_score=0.90,
        created_at="2026-09-15 16:05:00",
        expires_at="2026-09-16 09:15:00",
    )
    engine.submit_human_approval("PROP_TSLA", "RISK_OFFICER", True, "2026-09-16 08:30:00")
    ok2, msg2 = engine.revalidate_pre_open(
        proposal_id="PROP_TSLA",
        current_premarket_price=226.0,
        prev_close_price=220.0, # +2.72% gap (>1.5%)
        has_corporate_event=False,
    )
    assert ok2 is False
    assert prop2.status == AlphaBLiveApprovalStatus.REJECTED
    assert prop2.rejection_reason == AlphaBRejectionReasonCode.OVERNIGHT_GAP_EXCEEDED

    # Proposal 3: Corporate event detected -> REJECT
    prop3 = engine.create_live_proposal(
        proposal_id="PROP_AAPL",
        decision_date="2026-09-15",
        symbol="AAPL",
        notional_usd=333.33,
        signal_score=0.80,
        created_at="2026-09-15 16:05:00",
        expires_at="2026-09-16 09:15:00",
    )
    engine.submit_human_approval("PROP_AAPL", "RISK_OFFICER", True, "2026-09-16 08:30:00")
    ok3, msg3 = engine.revalidate_pre_open(
        proposal_id="PROP_AAPL",
        current_premarket_price=225.5,
        prev_close_price=225.0,
        has_corporate_event=True, # Earnings in window
    )
    assert ok3 is False
    assert prop3.status == AlphaBLiveApprovalStatus.REJECTED
    assert prop3.rejection_reason == AlphaBRejectionReasonCode.EVENT_RISK_DETECTED


def test_strategy_kill_switches_and_triple_book_matching():
    """Verifies strategy kill switches and triple-book matching (Live vs Paper vs Shadow)."""
    engine = AlphaBLiveGovernedEngine()

    # Kill switch tests
    engine.pause_strategy()
    assert engine.is_paused is True
    with pytest.raises(PermissionError, match="paused/locked"):
        engine.create_live_proposal("P1", "2026-09-15", "NVDA", 333.33, 0.8, "16:05:00", "09:15:00")

    # Triple book evaluation
    triple = engine.evaluate_triple_book_comparison(sessions=25)
    assert triple.sessions_evaluated == 25
    assert triple.completed_cohorts == 22
    assert triple.live_net_expectancy_bps == pytest.approx(10.80, rel=1e-2)
    assert triple.paper_net_expectancy_bps == pytest.approx(11.80, rel=1e-2)
    assert triple.shadow_net_expectancy_bps == pytest.approx(11.20, rel=1e-2)
    assert triple.live_paper_gap_bps == pytest.approx(-1.00, rel=1e-2)
    assert triple.live_shadow_gap_bps == pytest.approx(-0.40, rel=1e-2)
    assert triple.live_cost_break_even_multiplier == pytest.approx(3.00, rel=1e-2)
    assert triple.max_drawdown_live_usd <= 30.0
