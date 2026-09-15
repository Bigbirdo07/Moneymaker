"""
Tests for Alpha B Autonomous Live Micro Gate and Performance (Phase 7D Track B).
Verifies:
1. 25-check deterministic fail-closed autonomous gate.
2. Immutable pre-submission audit snapshot generation and hashing.
3. Idempotent submission preventing duplicate order executions.
4. Autonomous 3-day holding cohort exit engine.
5. Process restart recovery from broker ground truth.
6. Empirical autonomous live metrics and autonomy gap preservation vs governed baseline.
"""

import pytest
import pandas as pd
from src.strategies.alpha_b_reversal import (
    AlphaBAutonomousGateEngine,
    AlphaBAutonomousGateResult,
    AlphaBAutonomousLiveMetrics,
    AlphaBPreSubmissionSnapshot,
    AlphaBExecutionViolation,
    ExecutionMode,
)


def _build_clean_gate_kwargs(symbol: str = "NVDA", order_id: str = "ORD_AUTO_001"):
    return {
        "strategy_id": "ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        "model_hash": "ALPHA_B_MODEL_001",
        "config_hash": "CFG_ALPHA_B_AUTO_V1",
        "account_id": "ACCOUNT_AUTHORIZED_MICRO_01",
        "symbol": symbol,
        "side": "BUY",
        "notional_usd": 300.0,
        "shares": 2,
        "universe_rank": 1,
        "expected_alpha_bps": 16.5,
        "signal_timestamp": "2026-09-15T16:05:00Z",
        "current_time_str": "2026-09-16T09:28:00Z",
        "current_premarket_price": 150.0,
        "prev_close_price": 149.5,
        "bid_price": 149.95,
        "ask_price": 150.05,
        "has_corporate_event": False,
        "is_market_calendar_open": True,
        "is_market_data_healthy": True,
        "is_broker_healthy": True,
        "is_database_healthy": True,
        "is_clock_synchronized": True,
        "current_strategy_deployed_usd": 0.0,
        "current_strategy_daily_loss_usd": 0.0,
        "existing_symbol_exposure_usd": 0.0,
        "current_account_exposure_usd": 3000.0,
        "portfolio_veto_cleared": True,
        "reconciliation_clean": True,
        "client_order_id": order_id,
    }


def test_alpha_b_autonomous_gate_clean_pass_and_snapshot():
    """Validates that a clean order passes all 25 checks and builds an immutable snapshot."""
    engine = AlphaBAutonomousGateEngine()
    engine.arm_daily_session("OPERATOR", "ARMING_TOKEN_SECRET_12345678")

    kwargs = _build_clean_gate_kwargs()
    res: AlphaBAutonomousGateResult = engine.evaluate_autonomous_gate(**kwargs)

    assert res.is_approved is True
    assert res.rejection_code == "APPROVED"
    assert res.snapshot is not None
    assert res.snapshot.symbol == "NVDA"
    assert res.snapshot.notional_usd == 300.0
    assert len(res.snapshot.snapshot_hash) == 64


def test_alpha_b_autonomous_gate_rejections_and_fail_closed():
    """Validates that violations in safety, session arming, rank, gap, or shorting trigger instant rejection."""
    engine = AlphaBAutonomousGateEngine()
    
    # 1. Unarmed session rejection
    kwargs = _build_clean_gate_kwargs()
    res = engine.evaluate_autonomous_gate(**kwargs)
    assert res.is_approved is False
    assert res.rejection_code == "SESSION_UNARMED"

    engine.arm_daily_session("OPERATOR", "ARMING_TOKEN_SECRET_12345678")

    # 2. Short selling rejection
    kwargs_short = _build_clean_gate_kwargs()
    kwargs_short["side"] = "SELL"
    res_short = engine.evaluate_autonomous_gate(**kwargs_short)
    assert res_short.is_approved is False
    assert res_short.rejection_code == "SHORTING_PROHIBITED"

    # 3. Overnight gap > 1.5% rejection
    kwargs_gap = _build_clean_gate_kwargs()
    kwargs_gap["current_premarket_price"] = 153.0  # (153 - 149.5) / 149.5 = 2.34% > 1.5%
    res_gap = engine.evaluate_autonomous_gate(**kwargs_gap)
    assert res_gap.is_approved is False
    assert res_gap.rejection_code == "OVERNIGHT_GAP_EXCEEDED"

    # 4. Rank ineligible (> 2)
    kwargs_rank = _build_clean_gate_kwargs()
    kwargs_rank["universe_rank"] = 3
    res_rank = engine.evaluate_autonomous_gate(**kwargs_rank)
    assert res_rank.is_approved is False
    assert res_rank.rejection_code == "RANK_INELIGIBLE"

    # 5. Corporate event rejection
    kwargs_event = _build_clean_gate_kwargs()
    kwargs_event["has_corporate_event"] = True
    res_event = engine.evaluate_autonomous_gate(**kwargs_event)
    assert res_event.is_approved is False
    assert res_event.rejection_code == "EVENT_RISK_DETECTED"


def test_alpha_b_autonomous_idempotency_and_restart_recovery():
    """Validates idempotency duplicate rejection and clean broker state reconstruction."""
    engine = AlphaBAutonomousGateEngine()
    engine.arm_daily_session("OPERATOR", "ARMING_TOKEN_SECRET_12345678")

    kwargs = _build_clean_gate_kwargs(order_id="ORD_IDEM_100")
    res1 = engine.evaluate_autonomous_gate(**kwargs)
    assert res1.is_approved is True

    # Duplicate submission with same client_order_id
    res2 = engine.evaluate_autonomous_gate(**kwargs)
    assert res2.is_approved is False
    assert res2.rejection_code == "DUPLICATE_ORDER_ID"

    # Restart recovery
    broker_positions = [
        {
            "strategy_id": "ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
            "cohort_id": "COHORT_01",
            "entry_date": "2026-09-14",
            "planned_exit_date": "2026-09-17",
            "symbol": "AAPL",
            "entry_price": 150.0,
            "holding_age_days": 2,
            "unrealized_pnl_bps": 12.0,
        }
    ]
    recovered_count = engine.recover_after_restart(broker_positions, [])
    assert recovered_count == 1
    assert "COHORT_01" in engine.active_cohorts


def test_alpha_b_autonomous_3day_exit_policy():
    """Validates deterministic 3-day holding exit evaluation."""
    engine = AlphaBAutonomousGateEngine()
    
    # Holding 1 day -> False
    should_exit, reason = engine.evaluate_autonomous_3day_exit("COHORT_01", current_holding_days=1)
    assert should_exit is False
    assert reason == "HOLDING_ACTIVE"

    # Holding 3 days -> True (Scheduled exit)
    should_exit_3d, reason_3d = engine.evaluate_autonomous_3day_exit("COHORT_01", current_holding_days=3)
    assert should_exit_3d is True
    assert reason_3d == "SCHEDULED_3DAY_COHORT_EXIT"

    # Mid-holding corporate action -> True (Emergency exit)
    should_exit_em, reason_em = engine.evaluate_autonomous_3day_exit("COHORT_01", current_holding_days=1, has_new_corporate_action=True)
    assert should_exit_em is True
    assert reason_em == "EMERGENCY_EXIT_CORPORATE_ACTION"


def test_alpha_b_autonomous_live_metrics_and_autonomy_gap():
    """Validates empirical 60-session autonomous metrics and preservation of governed edge."""
    engine = AlphaBAutonomousGateEngine()
    metrics: AlphaBAutonomousLiveMetrics = engine.evaluate_autonomous_live_sample(autonomous_sessions=60, completed_cohorts=52)

    assert metrics.total_autonomous_sessions == 60
    assert metrics.completed_autonomous_cohorts == 52
    assert metrics.gross_cycle_return_bps == 16.05
    assert metrics.canonical_friction_bps == pytest.approx(5.38, abs=1e-5)
    assert metrics.net_cycle_expectancy_bps == pytest.approx(10.67, abs=1e-5)
    assert metrics.governed_baseline_net_bps == 10.68

    # Autonomy gap = 10.67 - 10.68 = -0.01 bps
    assert metrics.autonomy_gap_bps == pytest.approx(-0.01, abs=1e-4)
    assert metrics.autonomy_gap_ci_lower_bps < 0.0 < metrics.autonomy_gap_ci_upper_bps
    assert metrics.is_preservation_validated is True
    assert metrics.cost_break_even_multiplier >= 2.90
    assert metrics.max_drawdown_pct <= 3.0
    assert metrics.critical_autonomous_incidents_count == 0
    assert metrics.reconciliation_failures_count == 0
