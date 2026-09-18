"""Tests for MarketBreadthEngine (Phases E4, E5)."""

import pytest
from src.intelligence.market_breadth import MarketBreadthEngine
from src.intelligence.morning_market_state import DispersionState


def test_breadth_empty_universe():
    engine = MarketBreadthEngine()
    snapshot = engine.compute_breadth({}, {})
    assert snapshot.total_evaluated == 0
    assert snapshot.pct_positive_premarket == 50.0
    assert snapshot.dispersion_state == DispersionState.NORMAL


def test_breadth_normal_distribution():
    engine = MarketBreadthEngine()
    returns = {
        f"SYM_{i}": 0.5 if i % 3 != 0 else -0.4 for i in range(100)
    }
    vwap_dists = {
        f"SYM_{i}": 0.2 if i % 2 == 0 else -0.1 for i in range(100)
    }
    snapshot = engine.compute_breadth(returns, vwap_dists)
    assert snapshot.total_evaluated == 100
    assert snapshot.advancers_count == 66
    assert snapshot.decliners_count == 34
    assert snapshot.pct_positive_premarket == 66.0
    assert snapshot.pct_above_vwap == 50.0
    assert snapshot.dispersion_state in [DispersionState.NORMAL, DispersionState.LOW, DispersionState.HIGH]


def test_extreme_dispersion():
    engine = MarketBreadthEngine()
    # High variance returns
    returns = {
        "SYM_1": 15.0,
        "SYM_2": -12.0,
        "SYM_3": 8.0,
        "SYM_4": -10.0,
        "SYM_5": 5.0,
    }
    snapshot = engine.compute_breadth(returns, returns)
    assert snapshot.dispersion_state == DispersionState.EXTREME
    assert snapshot.cross_sectional_dispersion_bps > 250.0
