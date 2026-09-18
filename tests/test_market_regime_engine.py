"""Tests for MarketRegimeEngine (Phase E2)."""

import pytest
from src.intelligence.market_regime_engine import MarketRegimeEngine
from src.intelligence.morning_market_state import (
    DispersionState,
    MarketBreadthSnapshot,
    MarketRegime,
)


def test_bullish_continuation_regime():
    engine = MarketRegimeEngine()
    breadth = MarketBreadthSnapshot(
        pct_above_vwap=72.0,
        pct_positive_premarket=75.0,
        cross_sectional_dispersion_bps=120.0,
        dispersion_state=DispersionState.NORMAL,
        advancers_count=600,
        decliners_count=200,
        total_evaluated=800,
    )
    regime = engine.classify_regime(
        spy_overnight_return_pct=0.45,
        spy_premarket_return_pct=0.35,
        breadth=breadth,
        market_realized_vol_bps=90.0,
    )
    assert regime == MarketRegime.BULLISH_CONTINUATION


def test_bearish_continuation_regime():
    engine = MarketRegimeEngine()
    breadth = MarketBreadthSnapshot(
        pct_above_vwap=22.0,
        pct_positive_premarket=25.0,
        cross_sectional_dispersion_bps=130.0,
        dispersion_state=DispersionState.NORMAL,
        advancers_count=200,
        decliners_count=600,
        total_evaluated=800,
    )
    regime = engine.classify_regime(
        spy_overnight_return_pct=-0.65,
        spy_premarket_return_pct=-0.50,
        breadth=breadth,
        market_realized_vol_bps=110.0,
    )
    assert regime == MarketRegime.BEARISH_CONTINUATION


def test_high_vol_shock_regime():
    engine = MarketRegimeEngine()
    breadth = MarketBreadthSnapshot(
        pct_above_vwap=30.0,
        pct_positive_premarket=35.0,
        cross_sectional_dispersion_bps=380.0,
        dispersion_state=DispersionState.EXTREME,
        advancers_count=280,
        decliners_count=520,
        total_evaluated=800,
    )
    regime = engine.classify_regime(
        spy_overnight_return_pct=-1.80,
        spy_premarket_return_pct=-1.50,
        breadth=breadth,
        market_realized_vol_bps=260.0,
    )
    assert regime == MarketRegime.HIGH_VOL_SHOCK


def test_low_vol_chop_regime():
    engine = MarketRegimeEngine()
    breadth = MarketBreadthSnapshot(
        pct_above_vwap=50.0,
        pct_positive_premarket=51.0,
        cross_sectional_dispersion_bps=45.0,
        dispersion_state=DispersionState.LOW,
        advancers_count=405,
        decliners_count=395,
        total_evaluated=800,
    )
    regime = engine.classify_regime(
        spy_overnight_return_pct=0.02,
        spy_premarket_return_pct=-0.01,
        breadth=breadth,
        market_realized_vol_bps=45.0,
    )
    assert regime == MarketRegime.LOW_VOL_CHOP


def test_mean_reversion_regime():
    engine = MarketRegimeEngine()
    breadth = MarketBreadthSnapshot(
        pct_above_vwap=62.0,
        pct_positive_premarket=65.0,
        cross_sectional_dispersion_bps=110.0,
        dispersion_state=DispersionState.NORMAL,
        advancers_count=520,
        decliners_count=280,
        total_evaluated=800,
    )
    regime = engine.classify_regime(
        spy_overnight_return_pct=-0.55,
        spy_premarket_return_pct=-0.30,
        breadth=breadth,
        market_realized_vol_bps=95.0,
    )
    assert regime == MarketRegime.MEAN_REVERSION
