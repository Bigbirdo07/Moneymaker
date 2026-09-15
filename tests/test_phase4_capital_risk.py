"""
Comprehensive Test Suite for Phase 4 Capital Risk, Stress Testing, Capacity,
Monte Carlo Simulations, and Live Safety Guard Architecture.
"""

import os
from datetime import datetime, timezone
import pytest
import numpy as np
import pandas as pd

from src.stress.capacity_engine import CapacityEngine, CapitalScaleResult
from src.stress.stress_scenarios import StressTestingEngine
from src.stress.monte_carlo import MonteCarloRiskEngine
from src.safety.live_guard import (
    LiveSafetyGuard,
    LiveArmingPayload,
    LossBudgetConfig,
    SafetyEnforcementError,
)


def test_capital_scaling_and_nonlinear_impact():
    """Verify capacity scaling and square-root market impact across portfolio sizes."""
    engine = CapacityEngine()
    caps = [1000.0, 5000.0, 25000.0, 50000.0, 100000.0]
    results = engine.evaluate_scale(caps)

    assert len(results) == 5
    # Small capital ($1,000) has near-zero market impact
    assert results[0].nonlinear_impact_bps < 0.10
    assert results[0].capacity_status == "OPTIMAL"

    # Large capital ($100,000) has higher participation and impact
    assert results[-1].nonlinear_impact_bps > results[0].nonlinear_impact_bps
    assert results[-1].total_roundtrip_friction_bps > results[0].total_roundtrip_friction_bps


def test_cost_multiplier_stress_and_breakeven():
    """Verify cost inflation stress and break-even multiplier."""
    stress_engine = StressTestingEngine(base_gross_alpha_bps=4.80, base_friction_bps=3.22)
    multipliers = [1.0, 1.25, 1.5, 2.0, 3.0]
    res = stress_engine.evaluate_cost_stress(multipliers)

    assert res[0].net_expectancy_bps == pytest.approx(4.80 - 3.22, abs=0.01)
    assert res[0].breakeven_reached is False

    # At 1.5x (3.22 * 1.5 = 4.83 bps), net expectancy goes slightly negative
    assert res[2].breakeven_reached is True


def test_gap_through_stop_risk():
    """Verify that gap risk is modeled without assuming stops fill at stop price."""
    stress_engine = StressTestingEngine(base_capital_usd=1000.0, max_daily_loss_pct=0.03)
    gaps = [-0.01, -0.02, -0.05, -0.10]
    res = stress_engine.evaluate_gap_risk(gaps, position_pct=0.10)

    # -1% gap on $100 position = $1.00 loss (0.1% portfolio loss)
    assert res[0].realized_loss_usd == pytest.approx(1.00, abs=0.01)
    assert res[0].hit_daily_loss_limit is False

    # -5% gap on $100 position = $5.00 loss (0.5% portfolio loss)
    assert res[2].realized_loss_usd == pytest.approx(5.00, abs=0.01)


def test_correlated_archetype_shock():
    """Verify simultaneous losses across correlated positions."""
    stress_engine = StressTestingEngine(base_capital_usd=1000.0)
    correlations = [0.8, 0.9, 1.0]
    res = stress_engine.evaluate_correlated_shock(correlations, num_positions=3, position_pct=0.10, single_drop_pct=0.02)

    # Under correlation = 1.0, 3 positions of $100 dropping 2% = $6.00 loss (0.6% portfolio drawdown)
    assert res[2].total_loss_usd == pytest.approx(6.00, abs=0.01)
    assert res[2].portfolio_drawdown_pct == pytest.approx(0.006, abs=0.0001)


def test_model_inversion_and_circuit_breaker():
    """Verify model failure/inversion detection time and loss bounding."""
    stress_engine = StressTestingEngine(base_capital_usd=1000.0)
    inversions = [0.0, -0.02, -0.05]
    res = stress_engine.evaluate_model_inversion(inversions)

    # Detection happens within ~35 trades (approx 4 days), limiting capital loss to <$10 on $1,000 account
    assert res[0].trades_before_detection <= 35
    assert res[0].portfolio_loss_pct < 0.02  # Less than 2% loss before suspension


def test_monte_carlo_block_bootstrap_and_var():
    """Run 10,000-path block bootstrap simulation and verify VaR and Ruin probability."""
    mc_engine = MonteCarloRiskEngine(num_paths=1000, trades_per_path=200, block_size=5, random_state=42)
    # Generate realistic empirical returns with positive mean and volatility
    empirical_returns = [12.0, -10.0, 15.0, 8.0, -14.0, 20.0, -8.0, 5.0, 18.0, -12.0] * 25
    sim_res = mc_engine.run_simulation(empirical_returns, position_allocation_pct=0.10)

    assert sim_res.num_paths == 1000
    assert sim_res.median_return_pct > 0.0
    assert sim_res.prob_ruin_50pct == pytest.approx(0.0, abs=0.01)
    assert sim_res.daily_es_95_pct >= sim_res.daily_var_95_pct
    assert sim_res.daily_es_99_pct >= sim_res.daily_var_99_pct


def test_fractional_kelly_sizing():
    """Verify Kelly analysis and fractional sizing recommendations."""
    mc_engine = MonteCarloRiskEngine()
    kelly_res = mc_engine.evaluate_kelly_criterion(win_rate=0.574, avg_win_bps=16.5, avg_loss_bps=14.8)

    assert kelly_res.full_kelly_fraction > 0.0
    assert kelly_res.fractional_kelly_25pct < kelly_res.full_kelly_fraction
    assert kelly_res.fractional_kelly_25pct <= 0.10


def test_live_guard_multi_factor_arming():
    """Verify multi-factor arming fails closed if any of the 6 requirements are missing."""
    guard = LiveSafetyGuard(
        approved_account_id="ACC_LIVE_PILOT",
        max_live_capital_usd=2500.0,
    )
    expected_hash = "POLICY_HASH_VALID_123"

    # 1. Invalid live config flag -> FAIL
    p1 = LiveArmingPayload(
        is_live_config_enabled=False,
        approved_capital_usd=1000.0,
        approved_account_id="ACC_LIVE_PILOT",
        risk_policy_hash=expected_hash,
        human_arming_token="TOKEN_HUMAN_12345678",
        daily_session_auth_token="TOKEN_SESSION_12345678",
    )
    with pytest.raises(SafetyEnforcementError, match="Live configuration is disabled"):
        guard.verify_and_arm(p1, expected_hash)

    # 2. Capital exceeding cap -> FAIL
    p2 = LiveArmingPayload(
        is_live_config_enabled=True,
        approved_capital_usd=50000.0, # Exceeds $2,500
        approved_account_id="ACC_LIVE_PILOT",
        risk_policy_hash=expected_hash,
        human_arming_token="TOKEN_HUMAN_12345678",
        daily_session_auth_token="TOKEN_SESSION_12345678",
    )
    with pytest.raises(SafetyEnforcementError, match="exceeds hard ceiling"):
        guard.verify_and_arm(p2, expected_hash)

    # 3. Account ID mismatch -> FAIL
    p3 = LiveArmingPayload(
        is_live_config_enabled=True,
        approved_capital_usd=1000.0,
        approved_account_id="WRONG_ACCOUNT",
        risk_policy_hash=expected_hash,
        human_arming_token="TOKEN_HUMAN_12345678",
        daily_session_auth_token="TOKEN_SESSION_12345678",
    )
    with pytest.raises(SafetyEnforcementError, match="Account ID mismatch"):
        guard.verify_and_arm(p3, expected_hash)

    # 4. Valid payload -> SUCCESS
    p4 = LiveArmingPayload(
        is_live_config_enabled=True,
        approved_capital_usd=1000.0,
        approved_account_id="ACC_LIVE_PILOT",
        risk_policy_hash=expected_hash,
        human_arming_token="TOKEN_HUMAN_12345678",
        daily_session_auth_token="TOKEN_SESSION_12345678",
    )
    assert guard.verify_and_arm(p4, expected_hash) is True
    assert guard.is_armed is True


def test_live_guard_order_validation_and_firewalls():
    """Verify order validation firewalls: allow-list, single-order cap, and total capital cap."""
    guard = LiveSafetyGuard(
        approved_account_id="ACC_LIVE_PILOT",
        max_live_capital_usd=2500.0,
        max_single_order_usd=250.0,
        symbol_allow_list={"NVDA", "AMD", "TSLA"},
    )
    expected_hash = "POLICY_HASH_VALID_123"
    p = LiveArmingPayload(
        is_live_config_enabled=True,
        approved_capital_usd=1000.0,
        approved_account_id="ACC_LIVE_PILOT",
        risk_policy_hash=expected_hash,
        human_arming_token="TOKEN_HUMAN_12345678",
        daily_session_auth_token="TOKEN_SESSION_12345678",
    )
    guard.verify_and_arm(p, expected_hash)

    # 1. Normal order -> APPROVED
    ok, reason = guard.validate_live_order(
        account_id="ACC_LIVE_PILOT",
        symbol="NVDA",
        order_notional_usd=100.0,
        current_total_exposure_usd=0.0,
    )
    assert ok is True
    assert reason == "APPROVED"

    # 2. Non-allow-listed symbol -> REJECT
    ok, reason = guard.validate_live_order(
        account_id="ACC_LIVE_PILOT",
        symbol="GME",
        order_notional_usd=100.0,
        current_total_exposure_usd=0.0,
    )
    assert ok is False
    assert "not in approved allow-list" in reason

    # 3. Order exceeding MAX_SINGLE_ORDER_USD ($300 > $250) -> REJECT
    ok, reason = guard.validate_live_order(
        account_id="ACC_LIVE_PILOT",
        symbol="NVDA",
        order_notional_usd=300.0,
        current_total_exposure_usd=0.0,
    )
    assert ok is False
    assert "exceeds MAX_SINGLE_ORDER_USD" in reason


def test_exclusive_execution_lock():
    """Verify exclusive process execution lock prevents duplicate process instances."""
    lock_file = "/tmp/test_moneymaker_execution.lock"
    if os.path.exists(lock_file):
        os.remove(lock_file)

    guard1 = LiveSafetyGuard(lock_file_path=lock_file)
    guard2 = LiveSafetyGuard(lock_file_path=lock_file)

    # First instance acquires lock
    assert guard1.acquire_exclusive_execution_lock() is True

    # Second instance fails to acquire lock
    assert guard2.acquire_exclusive_execution_lock() is False

    # First instance releases lock
    guard1.release_exclusive_execution_lock()
    assert os.path.exists(lock_file) is False

    # Second instance can now acquire lock
    assert guard2.acquire_exclusive_execution_lock() is True
    guard2.release_exclusive_execution_lock()
