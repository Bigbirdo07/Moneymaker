"""Tests for strategy signal generation and baselines."""

import pytest
from src.core.types import SignalDirection
from src.data.loader import HistoricalDataLoader
from src.features.engine import FeatureEngine
from src.strategies.baselines import AlwaysCashStrategy, BuyAndHoldStrategy, RandomSignalStrategy
from src.strategies.momentum import BaselineMomentumStrategy
from src.strategies.mean_reversion import BaselineMeanReversionStrategy


def test_always_cash_strategy() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="SPY", num_days=1, seed=42)
    strat = AlwaysCashStrategy()
    signals = strat.generate_signals(df)
    assert len(signals) == len(df)
    assert all(s.direction == SignalDirection.NO_TRADE for s in signals)


def test_buy_and_hold_strategy() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="SPY", num_days=1, seed=42)
    strat = BuyAndHoldStrategy()
    signals = strat.generate_signals(df)
    assert len(signals) == len(df)
    assert signals[0].direction == SignalDirection.BUY
    assert all(s.direction == SignalDirection.HOLD for s in signals[1:])


def test_random_signal_strategy_reproducibility() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="SPY", num_days=1, seed=42)
    strat1 = RandomSignalStrategy(seed=100)
    strat2 = RandomSignalStrategy(seed=100)
    signals1 = strat1.generate_signals(df)
    signals2 = strat2.generate_signals(df)
    assert [s.direction for s in signals1] == [s.direction for s in signals2]


def test_momentum_strategy_signals() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="NVDA", num_days=3, seed=42)
    engine = FeatureEngine()
    features = engine.compute_all_features(df)
    
    strat = BaselineMomentumStrategy()
    signals = strat.generate_signals(features)
    assert len(signals) == len(features)
    # Strategy should produce valid Signal domain objects
    for s in signals:
        assert s.direction in (SignalDirection.BUY, SignalDirection.NO_TRADE)
        assert 0.0 <= s.confidence <= 1.0


def test_mean_reversion_strategy_signals() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AMD", num_days=3, seed=42)
    engine = FeatureEngine()
    features = engine.compute_all_features(df)
    
    strat = BaselineMeanReversionStrategy()
    signals = strat.generate_signals(features)
    assert len(signals) == len(features)
    for s in signals:
        assert s.direction in (SignalDirection.BUY, SignalDirection.NO_TRADE)
