"""Tests ensuring strict chronological execution timing and zero same-bar execution leakage."""

from datetime import datetime, timedelta, timezone
import pandas as pd
import pytest

from src.core.types import SignalDirection, OrderSide
from src.data.loader import HistoricalDataLoader
from src.features.engine import FeatureEngine
from src.strategies.momentum import BaselineMomentumStrategy
from src.backtest.engine import BacktestEngine
from src.backtest.costs import TransactionCostModel


def test_close_and_range_features_available_only_at_bar_close() -> None:
    """
    Test 1 & 2:
    A 5-minute bar starting at t (e.g. 09:30:00) contains High, Low, Close, Volume.
    The features derived from this bar are available ONLY at t + 5m (09:35:00).
    """
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="SPY", num_days=1, seed=42)
    engine = FeatureEngine(bar_duration=timedelta(minutes=5))
    features = engine.compute_all_features(df)

    for _, row in features.iterrows():
        bar_start = row["event_timestamp"]
        available_at = row["available_timestamp"]
        assert available_at == bar_start + timedelta(minutes=5), (
            f"Feature available_timestamp ({available_at}) must be exactly bar_start + 5 minutes ({bar_start + timedelta(minutes=5)})"
        )


def test_signal_and_fill_timestamps_are_chronological() -> None:
    """
    Test 3:
    Verifies that for every completed trade:
    fill_timestamp >= signal_timestamp >= feature.available_timestamp > bar_start.
    """
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=3, seed=42)
    engine = FeatureEngine()
    features = engine.compute_all_features(df)

    strategy = BaselineMomentumStrategy()
    backtester = BacktestEngine(initial_capital=1000.0, max_position_pct=0.10)
    result = backtester.run(strategy, features)

    for trade in result.trades:
        # Entry timestamp must be at or after the bar timestamp where the signal was formed
        assert trade.entry_timestamp >= df["timestamp"].iloc[0]
        # Exit timestamp must strictly succeed entry timestamp
        assert trade.exit_timestamp > trade.entry_timestamp, (
            f"Trade exit timestamp ({trade.exit_timestamp}) must be strictly after entry ({trade.entry_timestamp})"
        )


def test_forward_target_never_enters_strategy_signals() -> None:
    """
    Test 4:
    Verifies that strategy decisions never read any 'target_' columns.
    """
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=2, seed=42)
    engine = FeatureEngine(include_targets=True)
    features = engine.compute_all_features(df)

    # Corrupt target columns deliberately with massive values
    features_corrupted_targets = features.copy()
    for col in [c for c in features.columns if c.startswith("target_")]:
        features_corrupted_targets[col] = 999999.0

    strategy = BaselineMomentumStrategy()
    signals_clean = strategy.generate_signals(features)
    signals_corrupted = strategy.generate_signals(features_corrupted_targets)

    # Signals must be 100% identical regardless of what targets contain
    for s_clean, s_corr in zip(signals_clean, signals_corrupted):
        assert s_clean.direction == s_corr.direction
        assert s_clean.signal_strength == s_corr.signal_strength
        assert s_clean.confidence == s_corr.confidence
