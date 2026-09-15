"""Volume and microstructure features calculated with zero lookahead bias."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_volume_features(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Calculates relative volume, volume z-scores, and price-volume divergence metrics."""
    res = df.copy()
    vol = res["volume"]
    close = res["close"]

    # Rolling mean & std volume
    vol_mean = vol.rolling(window=window, min_periods=window).mean()
    vol_std = vol.rolling(window=window, min_periods=window).std()

    # Relative volume (RVOL)
    res["feature_relative_volume_20b"] = vol / (vol_mean + 1e-10)

    # Volume Z-Score
    res["feature_volume_zscore_20b"] = (vol - vol_mean) / (vol_std + 1e-10)

    # Volume Acceleration (1-bar change)
    res["feature_volume_acceleration"] = vol.pct_change(1)

    # VWAP deviation (if VWAP available, else approximated)
    if "vwap" in res.columns and not res["vwap"].isna().all():
        res["feature_vwap_deviation"] = (close - res["vwap"]) / res["vwap"]
    else:
        typical_price = (res["high"] + res["low"] + close) / 3.0
        rolling_vwap = (typical_price * vol).rolling(window=window, min_periods=1).sum() / (vol.rolling(window=window, min_periods=1).sum() + 1e-10)
        res["feature_vwap_deviation"] = (close - rolling_vwap) / rolling_vwap

    # Price-Volume correlation (5-bar rolling)
    ret_1b = close.pct_change(1)
    vol_chg = vol.pct_change(1)
    res["feature_price_volume_corr_5b"] = ret_1b.rolling(window=5, min_periods=5).corr(vol_chg)

    return res
