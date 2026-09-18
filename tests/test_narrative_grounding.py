"""Tests for Grounded Narrative Validator (Phase E17)."""

import pytest
from src.intelligence.morning_narrative_validator import MorningNarrativeValidator
from src.intelligence.morning_market_state import (
    MorningMarketState,
    MarketRegime,
    SessionGateState,
    MarketBreadthSnapshot,
    DispersionState,
    MorningRiskSummary,
)


def test_narrative_grounding_clean():
    validator = MorningNarrativeValidator()
    breadth = MarketBreadthSnapshot(
        pct_above_vwap=63.0,
        pct_positive_premarket=65.0,
        cross_sectional_dispersion_bps=120.0,
        dispersion_state=DispersionState.NORMAL,
        advancers_count=520,
        decliners_count=280,
        total_evaluated=800,
    )
    risk_sum = MorningRiskSummary(
        market_risk_level="NORMAL",
        volatility_risk_level="NORMAL",
        macro_risk_level="LOW",
        event_risk_level="NORMAL",
        liquidity_risk_level="LOW",
        portfolio_risk_level="NOMINAL",
        system_risk_level="READY",
        overall_risk_state="GO",
        primary_risks=["Standard market volatility"],
    )
    state = MorningMarketState(
        date_str="2026-09-18",
        timestamp="2026-09-18T08:45:00Z",
        portfolio_equity=1000.0,
        capital_tier="TIER_PAPER_1000",
        portfolio_risk_state="NORMAL",
        market_regime=MarketRegime.BULLISH_CONTINUATION,
        session_gate=SessionGateState.GO,
        spy_premarket_return_pct=0.31,
        spy_overnight_return_pct=0.25,
        breadth=breadth,
        strongest_sectors=[],
        weakest_sectors=[],
        raw_universe_count=4812,
        eligible_universe_count=2945,
        liquid_universe_count=826,
        quality_pass_count=803,
        event_veto_count=17,
        fast_scanner_count=64,
        deep_rank_count=12,
        entry_qualified_count=0,
        macro_events_today=[],
        top_candidates=[],
        risk_summary=risk_sum,
    )

    clean_narrative = (
        "Market regime is bullish continuation with positive momentum. "
        "Session gate is GO with normal deployment permitted. "
        "Breadth is positive across the universe."
    )
    res = validator.validate_narrative(clean_narrative, state)
    assert res.is_grounded
    assert len(res.violations) == 0


def test_narrative_grounding_rejects_gate_hallucination():
    validator = MorningNarrativeValidator()
    breadth = MarketBreadthSnapshot(
        pct_above_vwap=25.0,
        pct_positive_premarket=30.0,
        cross_sectional_dispersion_bps=120.0,
        dispersion_state=DispersionState.NORMAL,
        advancers_count=200,
        decliners_count=600,
        total_evaluated=800,
    )
    risk_sum = MorningRiskSummary(
        market_risk_level="ELEVATED",
        volatility_risk_level="NORMAL",
        macro_risk_level="LOW",
        event_risk_level="NORMAL",
        liquidity_risk_level="LOW",
        portfolio_risk_level="NOMINAL",
        system_risk_level="READY",
        overall_risk_state="NO_GO",
        primary_risks=["Adverse market regime"],
    )
    state = MorningMarketState(
        date_str="2026-09-18",
        timestamp="2026-09-18T08:45:00Z",
        portfolio_equity=1000.0,
        capital_tier="TIER_PAPER_1000",
        portfolio_risk_state="NORMAL",
        market_regime=MarketRegime.BEARISH_CONTINUATION,
        session_gate=SessionGateState.NO_GO,
        spy_premarket_return_pct=-1.2,
        spy_overnight_return_pct=-1.0,
        breadth=breadth,
        strongest_sectors=[],
        weakest_sectors=[],
        raw_universe_count=4812,
        eligible_universe_count=2945,
        liquid_universe_count=826,
        quality_pass_count=803,
        event_veto_count=17,
        fast_scanner_count=64,
        deep_rank_count=12,
        entry_qualified_count=0,
        macro_events_today=[],
        top_candidates=[],
        risk_summary=risk_sum,
    )

    hallucinated_narrative = (
        "Market regime is bullish. Session gate is GO. Deploy risk immediately."
    )
    res = validator.validate_narrative(hallucinated_narrative, state)
    assert not res.is_grounded
    assert len(res.violations) >= 1
    assert any("GATE_MISMATCH" in v for v in res.violations)
