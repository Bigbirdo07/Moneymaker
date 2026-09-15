"""
Tests for Phase 7E Governance Guardrails and Prohibitions.
"""

import pytest
import yaml
from src.llm.research_director import MoneymakerResearchDirector, LLMOutputType
from src.strategies.alpha_b_reversal import (
    AlphaBCapacityManager,
    AlphaBCapacityTier,
)
from src.portfolio.strategy_allocator_research import (
    StrategyAllocatorResearchEngine,
    AllocatorExecutionViolation,
)


def test_alpha_a_frozen_and_cannot_scale_above_10k():
    with open("configs/frozen_tier3.yaml", "r") as f:
        config = yaml.safe_load(f)
    assert config["strategy_id"] == "ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1"
    assert config["capital_specification"]["authorized_capital_usd"] == 10000.0



def test_frozen_alpha_b_tier0_and_tier1_configs():
    with open("configs/frozen_alpha_b_tier0.yaml", "r") as f:
        cfg0 = yaml.safe_load(f)
    assert cfg0["autonomous_risk_and_capital"]["authorized_live_capital_usd"] == 1000.0
    assert not cfg0["target_book"]["short_selling_permitted"]

    with open("configs/frozen_alpha_b_tier1.yaml", "r") as f:
        cfg1 = yaml.safe_load(f)
    assert cfg1["autonomous_risk_and_capital"]["authorized_live_capital_usd"] == 2500.0
    assert not cfg1["target_book"]["short_selling_permitted"]


def test_research_director_phase7e_methods_and_read_only_barrier():
    rd = MoneymakerResearchDirector()
    assert rd._is_read_only

    out1 = rd.generate_strategy_capacity_warning(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        current_capital_usd=1000.0,
        tested_capital_usd=2500.0,
        retention_pct=98.97,
        capacity_state="HEALTHY_CAPACITY",
    )
    assert out1.output_type == LLMOutputType.STRATEGY_CAPACITY_WARNING

    out2 = rd.generate_allocation_research_finding(
        policy_name="CAPPED_RISK_PARITY",
        annualized_return_pct=34.2,
        sharpe_ratio=6.45,
        max_drawdown_pct=1.45,
        avg_cash_pct=5.0,
    )
    assert out2.output_type == LLMOutputType.ALLOCATION_RESEARCH_FINDING

    out3 = rd.generate_allocation_overfit_warning(
        tested_configurations_count=18,
        holdout_sharpe_ratio=6.20,
        in_sample_sharpe_ratio=6.45,
    )
    assert out3.output_type == LLMOutputType.ALLOCATION_OVERFIT_WARNING

    out4 = rd.generate_capacity_constraint_warning(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        desired_capital_usd=5000.0,
        validated_capacity_usd=2500.0,
        residual_cash_usd=2500.0,
    )
    assert out4.output_type == LLMOutputType.CAPACITY_CONSTRAINT_WARNING

    out5 = rd.generate_cash_buffer_analysis(
        mean_cash_pct=12.5,
        p95_cash_pct=25.0,
        drawdown_cushion_bps=18.5,
    )
    assert out5.output_type == LLMOutputType.CASH_BUFFER_ANALYSIS


def test_allocator_cannot_enter_live_execution_path():
    allocator = StrategyAllocatorResearchEngine()
    allocator._is_executable = True
    with pytest.raises(AllocatorExecutionViolation):
        allocator._assert_non_executable()
