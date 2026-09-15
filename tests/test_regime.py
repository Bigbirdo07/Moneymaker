"""Tests for market regime classification and breakdown analysis."""

import pandas as pd
import pytest

from src.core.types import MarketRegime
from src.regime.classifier import MarketRegimeClassifier
from src.regime.analysis import RegimeAnalyzer


def test_regime_classifier() -> None:
    clf = MarketRegimeClassifier(vol_threshold_pct=0.18, trend_threshold_bps=5.0)

    # Bull High Vol row
    row_bull_hv = pd.Series({
        "feature_ema_cross_9_21": 0.0010,       # +10 bps trend
        "feature_realized_vol_20b": 0.0025,     # ~35% annualized vol
    })
    assert clf.classify_bar(row_bull_hv) == MarketRegime.BULL_HIGH_VOL

    # Bear Low Vol row
    row_bear_lv = pd.Series({
        "feature_ema_cross_9_21": -0.0010,      # -10 bps trend
        "feature_realized_vol_20b": 0.0005,     # ~7% annualized vol
    })
    assert clf.classify_bar(row_bear_lv) == MarketRegime.BEAR_LOW_VOL

    # Sideways row
    row_side = pd.Series({
        "feature_ema_cross_9_21": 0.0001,       # +1 bps trend
        "feature_realized_vol_20b": 0.0008,     # ~11% vol
    })
    assert clf.classify_bar(row_side) == MarketRegime.SIDEWAYS


def test_regime_analysis_breakdown() -> None:
    pred_df = pd.DataFrame({
        "regime": ["BULL_LOW_VOL"] * 10 + ["BEAR_HIGH_VOL"] * 10,
        "actual_label": [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
        "predicted_label": [1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        "p_up": [0.7, 0.6, 0.8, 0.65, 0.4, 0.75, 0.3, 0.7, 0.8, 0.45, 0.2, 0.3, 0.4, 0.25, 0.1, 0.7, 0.2, 0.3, 0.4, 0.2],
    })

    analyzer = RegimeAnalyzer()
    summary = analyzer.analyze_predictions_by_regime(pred_df)
    assert len(summary) == 2
    assert "accuracy" in summary.columns
    assert "brier_score" in summary.columns
