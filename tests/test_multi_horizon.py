"""Tests for multi-horizon return targets and signal decay analyzer."""

import pandas as pd
import pytest

from src.data.loader import HistoricalDataLoader
from src.features.returns import compute_target_returns
from src.features.engine import FeatureEngine
from src.evaluation.decay import SignalDecayAnalyzer
from src.strategies.momentum import BaselineMomentumStrategy


def test_multi_horizon_target_returns() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=3, seed=42)
    target_df = compute_target_returns(df, forward_bars=[1, 3, 6, 12], classification_thresholds_bps=[10.0, 15.0])

    assert "target_return_5m" in target_df.columns
    assert "target_return_15m" in target_df.columns
    assert "target_return_30m" in target_df.columns
    assert "target_return_60m" in target_df.columns
    assert "target_class_up_15m_10bps" in target_df.columns
    assert "target_class_3way_15m_10bps" in target_df.columns


def test_signal_decay_analyzer() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="NVDA", num_days=5, seed=42)
    engine = FeatureEngine()
    features = engine.compute_all_features(df)
    
    strat = BaselineMomentumStrategy()
    signals = strat.generate_signals(features)

    report = SignalDecayAnalyzer.compute_decay_curve(df, signals, model_id="mom_test")
    assert report.model_id == "mom_test"
    assert len(report.decay_curve) > 0
    assert report.peak_horizon_minutes >= 0
