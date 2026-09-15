"""
Tests for Phase 7F Governance Guardrails, Allocator Isolation, and Tier 3 Locking.
"""

import pytest
import yaml
from src.llm.research_director import MoneymakerResearchDirector, LLMOutputType
from src.strategies.alpha_b_reversal import (
    AlphaBCapacityManager,
    AlphaBCapacityTier,
)


def test_alpha_a_frozen_at_10k_invariance():
    with open("configs/frozen_tier3.yaml", "r") as f:
        config = yaml.safe_load(f)
    assert config["strategy_id"] == "ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1"
    assert config["capital_specification"]["authorized_capital_usd"] == 10000.0


def test_frozen_alpha_b_tier2_and_tier3_lock():
    with open("configs/frozen_alpha_b_tier2.yaml", "r") as f:
        cfg = yaml.safe_load(f)
    assert cfg["autonomous_risk_and_capital"]["authorized_live_capital_usd"] == 5000.0
    assert not cfg["target_book"]["short_selling_permitted"]

    manager = AlphaBCapacityManager(AlphaBCapacityTier.TIER_2)
    with pytest.raises(PermissionError, match="is LOCKED"):
        manager.attempt_tier3_or_higher(AlphaBCapacityTier.TIER_3)


def test_frozen_allocator_shadow_config():
    with open("configs/frozen_allocator_shadow_v1.yaml", "r") as f:
        cfg = yaml.safe_load(f)
    assert cfg["allocator_id"] == "STRATEGY_ALLOCATION_FORWARD_SHADOW"
    assert not cfg["execution_firewall"]["is_executable"]
    assert cfg["execution_firewall"]["prohibit_broker_adapter_imports"]
    assert cfg["execution_firewall"]["prohibit_live_capital_mutations"]


def test_research_director_phase7f_methods_and_read_only_barrier():
    rd = MoneymakerResearchDirector()
    assert rd._is_read_only

    out1 = rd.generate_alpha_capacity_mechanism_finding(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        primary_bottleneck="SIGNAL_SCARCITY",
        tested_capital_usd=5000.0,
        evidence_summary="Top-2 selection creates idle cash buffer.",
    )
    assert out1.output_type == LLMOutputType.ALPHA_CAPACITY_MECHANISM_FINDING

    out2 = rd.generate_signal_scarcity_finding(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        mean_candidates_per_day=3.2,
        mean_unused_slots=0.45,
        idle_cash_share_pct=21.2,
    )
    assert out2.output_type == LLMOutputType.SIGNAL_SCARCITY_FINDING

    out3 = rd.generate_cohort_concentration_warning(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        peak_symbol_concentration_pct=32.5,
        peak_sector_concentration_pct=48.2,
        resizing_events_count=8,
    )
    assert out3.output_type == LLMOutputType.COHORT_CONCENTRATION_WARNING

    out4 = rd.generate_allocation_forward_finding(
        policy_name="CAPPED_RISK_PARITY",
        forward_sharpe=7.81,
        forward_return_pct=38.90,
        forward_max_dd_pct=1.28,
        forward_turnover_pct=11.8,
    )
    assert out4.output_type == LLMOutputType.ALLOCATION_FORWARD_FINDING

    out5 = rd.generate_allocation_sharpe_decay_warning(
        policy_name="CAPPED_RISK_PARITY",
        research_sharpe=7.17,
        forward_sharpe=7.81,
        decay_pct=8.9,
    )
    assert out5.output_type == LLMOutputType.ALLOCATION_SHARPE_DECAY_WARNING

    out6 = rd.generate_portfolio_capacity_warning(
        total_account_capital_usd=15000.0,
        combined_gross_pct=46.5,
        overnight_gross_pct=12.2,
        veto_count=8,
    )
    assert out6.output_type == LLMOutputType.PORTFOLIO_CAPACITY_WARNING

    out7 = rd.generate_idle_capital_finding(
        authorized_capital_usd=5000.0,
        mean_deployed_usd=3940.0,
        mean_cash_usd=1060.0,
        cash_yield_opportunity_bps=12.5,
    )
    assert out7.output_type == LLMOutputType.IDLE_CAPITAL_FINDING
