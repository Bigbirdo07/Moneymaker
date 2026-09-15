"""Tests for corporate action handling, split adjustments, and discontinuity auditing."""

from datetime import datetime, timezone
import pandas as pd
import pytest

from src.data.corporate_actions import CorporateActionManager, StockSplitEvent
from src.data.loader import HistoricalDataLoader


def test_detect_unadjusted_split_anomaly() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="NVDA", num_days=2, initial_price=120.0, seed=42)
    
    # Artificially inject an unadjusted 2:1 stock split at bar 20 (price drops by 50%)
    df.loc[20:, "open"] /= 2.0
    df.loc[20:, "high"] /= 2.0
    df.loc[20:, "low"] /= 2.0
    df.loc[20:, "close"] /= 2.0
    df.loc[20:, "volume"] *= 2.0

    mgr = CorporateActionManager()
    anomalies = mgr.detect_unadjusted_split_anomalies(df)
    assert len(anomalies) >= 1
    assert anomalies[0]["suspected_action"] == "FORWARD_SPLIT"
    assert anomalies[0]["price_change_pct"] <= -0.40


def test_apply_split_adjustments() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=2, initial_price=200.0, seed=42)
    split_date = str(df["timestamp"].iloc[len(df) // 2].date())

    split_event = StockSplitEvent(symbol="AAPL", effective_date=split_date, ratio=2.0)
    mgr = CorporateActionManager(splits=[split_event])
    
    adjusted_df = mgr.apply_split_adjustments(df, [split_event])
    
    # Pre-split prices should be halved
    split_ts = pd.to_datetime(split_date, utc=True)
    mask_pre = pd.to_datetime(df["timestamp"], utc=True) < split_ts
    assert adjusted_df.loc[mask_pre, "close"].iloc[0] == pytest.approx(df.loc[mask_pre, "close"].iloc[0] / 2.0)
    assert adjusted_df.loc[mask_pre, "volume"].iloc[0] == pytest.approx(df.loc[mask_pre, "volume"].iloc[0] * 2.0)
