"""Tests for conservative execution fill models and trade cooldown."""

import pandas as pd
import pytest

from src.core.types import Signal, SignalDirection
from src.backtest.execution_research import ExecutionResearcher
from datetime import datetime, timezone


def test_trade_cooldown_suppresses_churn() -> None:
    signals = [
        Signal(symbol="AAPL", timestamp=datetime(2026, 1, 7, 14, i*5, tzinfo=timezone.utc), direction=SignalDirection.BUY, signal_strength=1.0, expected_return=0.01, confidence=0.7, expected_holding_period=6, model_version="v1")
        for i in range(10)
    ]
    
    # Apply cooldown of 4 bars (20 minutes)
    filtered = ExecutionResearcher.apply_trade_cooldown(signals, min_cooldown_bars=4)
    buy_count = sum(1 for s in filtered if s.direction == SignalDirection.BUY)
    
    # 10 consecutive buy signals with 4-bar cooldown -> bars 0, 4, 8 are BUY (3 total)
    assert buy_count == 3
    assert filtered[0].direction == SignalDirection.BUY
    assert filtered[1].direction == SignalDirection.NO_TRADE
    assert filtered[4].direction == SignalDirection.BUY
