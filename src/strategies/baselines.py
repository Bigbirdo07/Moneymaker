"""Mandatory baseline trading strategies for benchmarking sophisticated models."""

from __future__ import annotations

from typing import List, Optional
import numpy as np
import pandas as pd

from src.core.types import Signal, SignalDirection
from src.strategies.base import BaseStrategy


class AlwaysCashStrategy(BaseStrategy):
    """Benchmark strategy that always stays in cash (risk-free zero-return baseline)."""

    def __init__(self, name: str = "always_cash", version: str = "v1.0") -> None:
        super().__init__(name=name, version=version)

    def generate_signals(self, features_df: pd.DataFrame) -> List[Signal]:
        signals: List[Signal] = []
        for _, row in features_df.iterrows():
            signals.append(
                Signal(
                    symbol=str(row["symbol"]),
                    timestamp=row["timestamp"],
                    direction=SignalDirection.NO_TRADE,
                    signal_strength=0.0,
                    expected_return=0.0,
                    confidence=1.0,
                    expected_holding_period=0,
                    model_version=f"{self.name}_{self.version}",
                    metadata={"reason": "always_cash_baseline"},
                )
            )
        return signals


class BuyAndHoldStrategy(BaseStrategy):
    """Benchmark strategy that buys at start and holds (passive market benchmark)."""

    def __init__(self, name: str = "buy_and_hold", version: str = "v1.0") -> None:
        super().__init__(name=name, version=version)

    def generate_signals(self, features_df: pd.DataFrame) -> List[Signal]:
        signals: List[Signal] = []
        n = len(features_df)
        for idx, (_, row) in enumerate(features_df.iterrows()):
            if idx == 0:
                direction = SignalDirection.BUY
                strength = 1.0
            else:
                direction = SignalDirection.HOLD
                strength = 0.5
            
            signals.append(
                Signal(
                    symbol=str(row["symbol"]),
                    timestamp=row["timestamp"],
                    direction=direction,
                    signal_strength=strength,
                    expected_return=0.001,
                    confidence=1.0,
                    expected_holding_period=n - idx,
                    model_version=f"{self.name}_{self.version}",
                    metadata={"strategy": "buy_and_hold"},
                )
            )
        return signals


class RandomSignalStrategy(BaseStrategy):
    """Benchmark strategy generating pseudorandom trading signals to test for pure noise."""

    def __init__(
        self,
        name: str = "random_predictor",
        version: str = "v1.0",
        buy_probability: float = 0.10,
        seed: int = 42,
    ) -> None:
        super().__init__(name=name, version=version)
        self.buy_probability = buy_probability
        self.seed = seed

    def generate_signals(self, features_df: pd.DataFrame) -> List[Signal]:
        rng = np.random.default_rng(self.seed)
        signals: List[Signal] = []
        for _, row in features_df.iterrows():
            roll = rng.random()
            if roll < self.buy_probability:
                direction = SignalDirection.BUY
                strength = float(rng.uniform(0.5, 1.0))
                exp_ret = float(rng.uniform(0.002, 0.008))
                conf = float(rng.uniform(0.5, 0.7))
            else:
                direction = SignalDirection.NO_TRADE
                strength = 0.0
                exp_ret = 0.0
                conf = 0.5

            signals.append(
                Signal(
                    symbol=str(row["symbol"]),
                    timestamp=row["timestamp"],
                    direction=direction,
                    signal_strength=strength,
                    expected_return=exp_ret,
                    confidence=conf,
                    expected_holding_period=12,
                    model_version=f"{self.name}_{self.version}",
                    metadata={"random_seed": self.seed},
                )
            )
        return signals
