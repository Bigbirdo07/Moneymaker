"""
Tests for Phase 7D Multi-Strategy Governance, Kill Switches, and Invariants.
Verifies:
1. Emergency kill switch triggers instant lock and requires human rearming token.
2. Configuration freeze integrity and parameter invariance.
3. ResearchDirector strictly read-only barrier and analytical tool outputs.
4. Total account capital isolation and non-executable allocator boundaries.
"""

import pytest
import yaml
from src.strategies.alpha_b_reversal import (
    AlphaBAutonomousGateEngine,
    AlphaBExecutionViolation,
    ExecutionMode,
)
from src.llm.research_director import (
    MoneymakerResearchDirector,
    LLMOutputType,
)
from src.portfolio.multi_strategy_research import PortfolioRiskAggregator


def test_emergency_kill_switch_and_human_rearming_workflow():
    """Validates that emergency kill switch immediately blocks orders and requires valid human rearming token."""
    engine = AlphaBAutonomousGateEngine()
    engine.arm_daily_session("OPERATOR", "INITIAL_ARMING_TOKEN_12345678")
    assert engine.is_session_armed is True

    # Trigger emergency kill switch
    engine.trigger_emergency_kill_switch()
    assert engine.is_locked is True
    assert engine.is_paused is True
    assert engine.is_session_armed is False

    # Attempt rearming with invalid/short token -> Fails
    with pytest.raises(PermissionError, match="token rejected"):
        engine.human_rearm_after_suspension("short_tok")

    # Valid rearm token -> Re-enabled
    engine.human_rearm_after_suspension("VALID_HUMAN_REARM_TOKEN_87654321")
    assert engine.is_locked is False
    assert engine.is_paused is False
    assert engine.is_session_armed is True


def test_frozen_alpha_b_autonomous_config_invariance():
    """Validates YAML configuration matches frozen specifications."""
    with open("configs/frozen_alpha_b_autonomous_v1.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    assert cfg["strategy_id"] == "ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1"
    assert cfg["autonomous_risk_and_capital"]["authorized_live_capital_usd"] == 1000.0
    assert cfg["autonomous_risk_and_capital"]["max_single_position_usd"] == 333.33
    assert cfg["autonomous_risk_and_capital"]["max_overlapping_cohorts"] == 3
    assert cfg["autonomous_risk_and_capital"]["max_overnight_gap_pct"] == 0.015
    assert cfg["autonomous_risk_and_capital"]["human_per_trade_approval_required"] is False
    assert cfg["target_book"]["short_selling_permitted"] is False


def test_research_director_phase7d_methods_and_read_only_barrier():
    """Confirms ResearchDirector remains read-only and generates structured Phase 7D findings."""
    rd = MoneymakerResearchDirector()
    assert rd.is_read_only is True

    # Autonomous Execution Finding
    auto_out = rd.generate_autonomous_execution_finding(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        autonomous_net_bps=10.67,
        governed_baseline_bps=10.68,
        autonomy_gap_bps=-0.01,
        sessions_count=60,
    )
    assert auto_out.output_type == LLMOutputType.AUTONOMOUS_EXECUTION_FINDING
    assert "preservation of quantitative edge" in auto_out.summary

    # Autonomy Degradation Warning
    deg_out = rd.generate_autonomy_degradation_warning(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        observed_net_bps=10.67,
        threshold_bps=3.0,
    )
    assert deg_out.output_type == LLMOutputType.AUTONOMY_DEGRADATION_WARNING


def test_portfolio_risk_aggregator_capital_hierarchy_invariance():
    """Validates that aggregate risk limits remain static across Alpha A ($10k) and Alpha B ($1k)."""
    agg = PortfolioRiskAggregator()
    assert agg.TOTAL_ACCOUNT_CAPITAL_USD == 11000.0
    assert agg.budgets["ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1"].authorized_capital_usd == 10000.0
    assert agg.budgets["ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL"].authorized_capital_usd == 1000.0
