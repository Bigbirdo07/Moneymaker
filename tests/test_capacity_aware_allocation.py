"""
Tests for Capacity-Aware Allocation and Cash Residual Logic (Phase 7E).
"""

import pytest
from src.portfolio.strategy_allocator_research import (
    StrategyAllocatorResearchEngine,
    StrategyCapacityConstraints,
)


def test_capacity_bounding_forces_cash_residual():
    # Account total capital = $20,000 USD
    # Strategy capacity limits: A = $10,000 max, B = $2,500 max
    constraints = StrategyCapacityConstraints(
        alpha_a_max_capital_usd=10000.0,
        alpha_b_max_capital_usd=2500.0,
        total_portfolio_capital_usd=20000.0,
    )
    engine = StrategyAllocatorResearchEngine(constraints=constraints)

    # Desired 70% A ($14,000), 30% B ($6,000)
    weights = engine.compute_capacity_aware_weights(raw_weight_a=0.70, raw_weight_b=0.30, total_capital=20000.0)

    # Capping checks
    assert weights.alpha_a_capital_usd == 10000.0  # Capped at $10k
    assert weights.alpha_b_capital_usd == 2500.0   # Capped at $2.5k
    assert weights.cash_capital_usd == 7500.0      # Residual cash: $20k - $12.5k = $7.5k

    # Effective percentage checks
    assert abs(weights.weight_alpha_a - 0.50) < 1e-4   # $10k / $20k = 50%
    assert abs(weights.weight_alpha_b - 0.125) < 1e-4  # $2.5k / $20k = 12.5%
    assert abs(weights.weight_cash - 0.375) < 1e-4     # $7.5k / $20k = 37.5%
    assert weights.is_capacity_constrained

    # Sum of weights must equal 100% (Zero leverage)
    assert abs((weights.weight_alpha_a + weights.weight_alpha_b + weights.weight_cash) - 1.0) < 1e-5


def test_unconstrained_allocation_has_zero_cash_residual():
    # Account total capital = $11,000 USD
    constraints = StrategyCapacityConstraints(
        alpha_a_max_capital_usd=10000.0,
        alpha_b_max_capital_usd=2500.0,
        total_portfolio_capital_usd=11000.0,
    )
    engine = StrategyAllocatorResearchEngine(constraints=constraints)

    # 90.91% A ($10,000), 9.09% B ($1,000)
    weights = engine.compute_capacity_aware_weights(raw_weight_a=0.90909, raw_weight_b=0.09091, total_capital=11000.0)

    assert abs(weights.alpha_a_capital_usd - 10000.0) < 1.0
    assert abs(weights.alpha_b_capital_usd - 1000.0) < 1.0
    assert abs(weights.cash_capital_usd - 0.0) < 1.0
    assert weights.weight_cash < 0.001
