"""Tests for market data quality and anomaly detection."""

from datetime import datetime, timedelta, timezone
import pandas as pd
import pytest

from src.data.loader import HistoricalDataLoader
from src.data.validation import DataValidator


def test_valid_synthetic_dataset_passes() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=2, seed=42)
    validator = DataValidator()
    report = validator.validate(df, symbol="AAPL")
    assert report.is_valid is True
    assert len(report.issues) == 0
    assert report.total_rows > 0


def test_missing_columns_fails() -> None:
    df = pd.DataFrame({"timestamp": [datetime.now(timezone.utc)], "close": [150.0]})
    validator = DataValidator()
    report = validator.validate(df, symbol="AAPL")
    assert report.is_valid is False
    assert any(iss.category == "MISSING_COLUMNS" for iss in report.issues)


def test_duplicate_timestamps_detected() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=1, seed=42)
    # Duplicate first row
    dup_df = pd.concat([df.iloc[:1], df]).reset_index(drop=True)
    validator = DataValidator()
    report = validator.validate(dup_df, symbol="AAPL")
    assert report.is_valid is False
    assert any(iss.category == "DUPLICATE_TIMESTAMPS" for iss in report.issues)


def test_out_of_order_timestamps_detected() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=1, seed=42)
    # Shuffle order
    shuffled_df = df.iloc[::-1].reset_index(drop=True)
    validator = DataValidator()
    report = validator.validate(shuffled_df, symbol="AAPL")
    assert report.is_valid is False
    assert any(iss.category == "OUT_OF_ORDER_TIMESTAMPS" for iss in report.issues)


def test_impossible_ohlc_detected() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=1, seed=42)
    # Invert high and low on row 5
    df.loc[5, "high"] = df.loc[5, "low"] - 1.0
    validator = DataValidator()
    report = validator.validate(df, symbol="AAPL")
    assert report.is_valid is False
    assert any(iss.category == "IMPOSSIBLE_HIGH_LOW" for iss in report.issues)


def test_negative_volume_detected() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=1, seed=42)
    df.loc[3, "volume"] = -500.0
    validator = DataValidator()
    report = validator.validate(df, symbol="AAPL")
    assert report.is_valid is False
    assert any(iss.category == "NEGATIVE_VOLUME" for iss in report.issues)


def test_extreme_price_gap_detected() -> None:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=1, seed=42)
    # 50% price spike in single bar
    df.loc[4, "close"] = df.loc[4, "close"] * 1.50
    df.loc[4, "high"] = df.loc[4, "close"] * 1.05
    validator = DataValidator(max_price_gap_pct=0.20)
    report = validator.validate(df, symbol="AAPL")
    assert report.is_valid is False
    assert any(iss.category == "EXTREME_PRICE_GAP" for iss in report.issues)
