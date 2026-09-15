"""Market data schema definition and validation models."""

from __future__ import annotations

from typing import List, Optional
import pandas as pd
from pydantic import BaseModel, Field


REQUIRED_OHLCV_COLUMNS = [
    "timestamp",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
]

OPTIONAL_MARKET_COLUMNS = [
    "vwap",
    "bid",
    "ask",
    "spread",
    "trade_count",
]


class MarketDataSchema:
    """Utilities for validating DataFrame schemas against standard market data format."""

    @staticmethod
    def validate_columns(df: pd.DataFrame) -> List[str]:
        """Returns missing required columns, if any."""
        missing = [col for col in REQUIRED_OHLCV_COLUMNS if col not in df.columns]
        return missing

    @staticmethod
    def enforce_types(df: pd.DataFrame) -> pd.DataFrame:
        """Enforces canonical data types on the market data dataframe."""
        df = df.copy()
        if "timestamp" in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
                df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            elif df["timestamp"].dt.tz is None:
                df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
            else:
                df["timestamp"] = df["timestamp"].dt.tz_convert("UTC")

        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].astype(str)

        numeric_cols = ["open", "high", "low", "close", "volume", "vwap", "bid", "ask", "spread"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "trade_count" in df.columns:
            df["trade_count"] = pd.to_numeric(df["trade_count"], errors="coerce")

        return df
