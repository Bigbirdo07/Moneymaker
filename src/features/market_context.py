"""Market context, benchmark relative performance, and intraday time features."""

from __future__ import annotations

from typing import Dict, Optional
import numpy as np
import pandas as pd
from src.data.calendar import TradingCalendar


def compute_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes session-aware time features (minute from open, minute to close, day of week)."""
    res = df.copy()
    ts = pd.to_datetime(res["timestamp"], utc=True)

    # Convert to NY time for market session metrics
    ny_ts = ts.dt.tz_convert("America/New_York")

    # Day of week (0 = Monday, 4 = Friday)
    res["feature_day_of_week"] = ny_ts.dt.dayofweek

    # Minutes from market open (09:30 ET)
    open_minutes = (ny_ts.dt.hour - 9) * 60 + (ny_ts.dt.minute - 30)
    res["feature_minutes_from_open"] = open_minutes.clip(lower=0)

    # Minutes to market close (16:00 ET = 390 minutes from open)
    res["feature_minutes_to_close"] = (390 - res["feature_minutes_from_open"]).clip(lower=0)

    return res


def compute_market_relative_features(
    asset_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    benchmark_symbol: str = "SPY",
) -> pd.DataFrame:
    """Computes relative strength and alpha metrics relative to a market benchmark (e.g. SPY)."""
    res = asset_df.copy()
    
    # Merge benchmark returns aligned strictly on UTC timestamp
    bench_sub = benchmark_df[["timestamp", "close"]].copy()
    bench_sub = bench_sub.rename(columns={"close": f"{benchmark_symbol}_close"})
    bench_sub[f"feature_{benchmark_symbol}_return_1b"] = bench_sub[f"{benchmark_symbol}_close"].pct_change(1)
    bench_sub[f"feature_{benchmark_symbol}_return_6b"] = bench_sub[f"{benchmark_symbol}_close"].pct_change(6)

    merged = pd.merge(res, bench_sub, on="timestamp", how="left")
    
    # Relative strength (asset return minus benchmark return)
    asset_ret_1b = merged["close"].pct_change(1)
    asset_ret_6b = merged["close"].pct_change(6)

    merged[f"feature_rel_strength_{benchmark_symbol}_1b"] = asset_ret_1b - merged[f"feature_{benchmark_symbol}_return_1b"]
    merged[f"feature_rel_strength_{benchmark_symbol}_6b"] = asset_ret_6b - merged[f"feature_{benchmark_symbol}_return_6b"]

    return merged
