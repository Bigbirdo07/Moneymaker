"""Tests for two-stage meta-labeling trade filter."""

import numpy as np
import pandas as pd
import pytest

from src.models.meta_labeling import MetaLabelingFilter


def test_meta_labeling_fit_and_filter() -> None:
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "feature_rsi_14": np.random.uniform(30, 70, size=n),
        "feature_atr_pct": np.random.uniform(0.002, 0.010, size=n),
        "feature_relative_volume_20b": np.random.uniform(0.8, 2.5, size=n),
        "feature_vwap_deviation": np.random.normal(0, 0.002, size=n),
    })
    primary_probs = np.random.uniform(0.52, 0.70, size=n)
    
    # Simulate trade outcomes: higher RVOL and higher prob correlated with profitability
    realized_net_returns = (df["feature_relative_volume_20b"] - 1.2) * 0.01 + np.random.normal(0, 0.005, size=n)

    filter_model = MetaLabelingFilter(n_estimators=20, max_depth=3, min_meta_probability=0.50)
    filter_model.fit_meta_model(df.iloc[:60], primary_probs[:60], realized_net_returns[:60])
    assert filter_model.is_fitted is True

    report = filter_model.evaluate_filter(df.iloc[60:], primary_probs[60:], realized_net_returns[60:])
    assert report.total_raw_candidates == 40
    assert report.approved_trades <= report.total_raw_candidates
