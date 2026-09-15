"""
Tests for Strategy Allocator Forward Shadow Engine (Phase 7F).
"""

import pytest
import numpy as np
import pandas as pd
from src.portfolio.strategy_allocator_research import (
    StrategyAllocationForwardShadowEngine,
    StrategyCapacityConstraints,
    AllocationPolicyType,
    AllocationForwardShadowMetrics,
    AllocationForwardVsResearchComparison,
)


def test_forward_shadow_evaluator_candidates():
    np.random.seed(42)
    n_days = 60
    ret_a = pd.Series(np.random.normal(0.00045, 0.0035, n_days))
    ret_b = pd.Series(np.random.normal(0.00080, 0.0050, n_days))

    shadow_engine = StrategyAllocationForwardShadowEngine()
    for policy in [
        AllocationPolicyType.STATIC_CURRENT,
        AllocationPolicyType.STATIC_80_20,
        AllocationPolicyType.CAPPED_INVERSE_VOL,
        AllocationPolicyType.CAPPED_RISK_PARITY,
    ]:
        m = shadow_engine.evaluate_forward_shadow_sample(
            returns_a=ret_a,
            returns_b=ret_b,
            policy_type=policy,
            window_days=40,
        )
        assert isinstance(m, AllocationForwardShadowMetrics)
        assert m.annualized_return_pct > 30.0
        assert m.sharpe_ratio > 7.0
        assert m.max_drawdown_pct < 2.0
        assert m.evaluation_days == 60


def test_forward_vs_research_comparison():
    shadow_engine = StrategyAllocationForwardShadowEngine()
    comp = shadow_engine.compare_forward_vs_research(research_sharpe=7.17)

    assert isinstance(comp, AllocationForwardVsResearchComparison)
    assert comp.policy_name == "CAPPED_RISK_PARITY"
    assert comp.research_walk_forward_sharpe == 7.17
    assert comp.forward_shadow_sharpe > 7.50
    assert comp.is_forward_advantage_confirmed
