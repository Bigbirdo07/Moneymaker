"""Tests for MorningBriefService and DeterministicMorningBriefRenderer (Phases E1, E15, E18)."""

import pytest
from src.intelligence.morning_brief import MorningBriefService
from src.intelligence.morning_brief_renderer import DeterministicMorningBriefRenderer
from src.intelligence.morning_market_state import (
    MorningMarketState,
    MarketRegime,
    SessionGateState,
    DispersionState,
)
from src.risk.portfolio_risk_state import PortfolioRiskState
from src.risk.capital_tiers import CapitalTier


def test_morning_brief_generation_and_render():
    portfolio = PortfolioRiskState.create(
        timestamp="2026-09-18T08:45:00Z",
        starting_day_equity=1000.0,
        current_equity=1000.0,
        cash=1000.0,
        peak_equity=1000.0,
        realized_pnl_today=0.0,
    )
    service = MorningBriefService()

    symbol_returns = {
        "NVDA": 1.45,
        "AMD": 1.80,
        "AVGO": 1.20,
        "CRM": 0.85,
        "ORCL": 0.65,
        "XOM": -0.30,
        "CVX": -0.45,
        "JNJ": -0.15,
    }
    vwap_dists = {sym: ret * 0.5 for sym, ret in symbol_returns.items()}
    sectors = {
        "NVDA": "Semiconductors",
        "AMD": "Semiconductors",
        "AVGO": "Semiconductors",
        "CRM": "Software",
        "ORCL": "Software",
        "XOM": "Energy",
        "CVX": "Energy",
        "JNJ": "Healthcare",
    }
    rel_vol = {sym: 2.5 if ret > 0 else 0.8 for sym, ret in symbol_returns.items()}
    scanner_syms = ["AMD", "NVDA", "AVGO", "CRM", "ORCL"]

    state = service.generate_morning_state(
        date_str="2026-09-18",
        timestamp="2026-09-18T08:45:00Z",
        portfolio_state=portfolio,
        spy_premarket_return_pct=0.31,
        spy_overnight_return_pct=0.25,
        symbol_returns_pct=symbol_returns,
        symbol_vwap_distances_pct=vwap_dists,
        symbol_sectors=sectors,
        symbol_rel_vol=rel_vol,
        scanner_symbols=scanner_syms,
    )

    assert state.date_str == "2026-09-18"
    assert state.portfolio_equity == 1000.0
    assert state.market_regime == MarketRegime.BULLISH_CONTINUATION
    assert state.session_gate in [SessionGateState.GO, SessionGateState.CAUTION]
    assert len(state.top_candidates) > 0
    assert state.provenance_hash != ""

    # Test serialization
    state_dict = state.to_dict()
    assert state_dict["capital_tier"] == "TIER_PAPER_1000"
    assert state_dict["portfolio_equity"] == 1000.0

    # Test deterministic rendering
    rendered = DeterministicMorningBriefRenderer.render(state)
    assert "MONEYMAKER MORNING BRIEF" in rendered
    assert "Portfolio Equity:\n$1,000.00" in rendered
    assert "AMD" in rendered
    assert "BULLISH_CONTINUATION" in rendered
