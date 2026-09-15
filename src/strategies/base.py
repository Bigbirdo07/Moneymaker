"""Abstract base strategy class and signal generator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd

from src.core.types import Signal, SignalDirection


class BaseStrategy(ABC):
    """Abstract base class for all systematic strategies and baseline models."""

    def __init__(self, name: str, version: str = "v1.0") -> None:
        self.name = name
        self.version = version

    @abstractmethod
    def generate_signals(self, features_df: pd.DataFrame) -> List[Signal]:
        """
        Generates quantitative trading signals from a chronological features dataframe.
        Must produce one Signal per bar/observation.
        """
        pass

    def evaluate_bar(self, row: pd.Series) -> Signal:
        """
        Evaluates a single market observation in real-time or streaming paper mode.
        Default implementation converts single row to DataFrame and calls generate_signals.
        """
        df = pd.DataFrame([row])
        signals = self.generate_signals(df)
        return signals[0] if signals else Signal(
            symbol=str(row.get("symbol", "UNKNOWN")),
            timestamp=row.get("timestamp"),
            direction=SignalDirection.NO_TRADE,
            signal_strength=0.0,
            expected_return=0.0,
            confidence=0.0,
            expected_holding_period=0,
            model_version=f"{self.name}_{self.version}",
        )
