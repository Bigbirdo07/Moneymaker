"""
Tests for Strategy Allocator Research Engine (Phase 7E).
"""

import pytest
import numpy as np
import pandas as pd
from src.portfolio.strategy_allocator_research import (
    StrategyAllocatorResearchEngine,
    StrategyCapacityConstraints,
    AllocationPolicyType,
    RebalanceFrequency,
    AllocationResearchVerdict,
    AllocatorExecutionViolation,
)


def test_research_allocator_non_executable_invariant():
    engine = StrategyAllocatorResearchEngine()
    assert not engine._is_executable
    # Internal assertion check
    engine._assert_non_executable()


def test_walk_forward_evaluation_across_baselines():
    np.random.seed(42)
    n_days = 60
    # Create realistic synthetic returns
    ret_a = pd.Series(np.random.normal(0.00045, 0.0035, n_days))
    ret_b = pd.Series(np.random.normal(0.00080, 0.0050, n_days))

    engine = StrategyAllocatorResearchEngine()
    for policy in [
        AllocationPolicyType.STATIC_90_10,
        AllocationPolicyType.STATIC_80_20,
        AllocationPolicyType.STATIC_70_30,
        AllocationPolicyType.CAPPED_RISK_PARITY,
    ]:
        m = engine.evaluate_allocation_policy(
            policy_type=policy,
            returns_a=ret_a,
            returns_b=ret_b,
            window_days=20,
            rebalance_freq=RebalanceFrequency.WEEKLY,
        )
        assert m.annualized_return_pct > 0.0
        assert m.annualized_volatility_pct > 0.0
        assert m.sharpe_ratio > 0.0
        assert m.max_drawdown_pct < 10.0
        assert m.weight_turnover_annualized_pct >= 0.0
        assert m.alpha_a_vol_contribution_pct > 0.0
        assert m.alpha_b_vol_contribution_pct > 0.0


def test_risk_parity_weight_bounds():
    engine = StrategyAllocatorResearchEngine()
    # High vol B vs Low vol A
    w_a, w_b = engine.compute_risk_parity_weights(vol_a=0.05, vol_b=0.15)
    assert w_a > w_b
    assert 0.50 <= w_a <= 0.95
    assert 0.05 <= w_b <= 0.50
    assert abs((w_a + w_b) - 1.0) < 1e-5


def test_allocator_stress_testing_scenarios():
    np.random.seed(42)
    n_days = 60
    ret_a = pd.Series(np.random.normal(0.00045, 0.0035, n_days))
    ret_b = pd.Series(np.random.normal(0.00080, 0.0050, n_days))

    engine = StrategyAllocatorResearchEngine()
    base_m = engine.evaluate_allocation_policy(
        AllocationPolicyType.CAPPED_RISK_PARITY,
        ret_a,
        ret_b,
        window_days=20,
    )
    stresses = engine.evaluate_stress_scenarios(base_m, ret_a, ret_b)
    assert len(stresses) == 5
    scenario_names = [s.scenario_name for s in stresses]
    assert "ALPHA_A_ZERO_EXPECTANCY" in scenario_names
    assert "ALPHA_B_ZERO_EXPECTANCY" in scenario_names
    assert "CORRELATION_SPIKE_POS_80" in scenario_names
    assert "ALPHA_A_FRICTION_PLUS_50PCT" in scenario_names
    assert "ALPHA_B_OVERNIGHT_GAP_SHOCK_2PCT" in scenario_names
