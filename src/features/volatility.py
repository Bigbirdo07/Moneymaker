"""Volatility features and estimators computed with zero lookahead bias."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculates Average True Range (ATR)."""
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    return atr


def compute_garman_klass_volatility(df: pd.DataFrame, period: int = 24) -> pd.Series:
    """
    Garman-Klass range-based volatility estimator:
    0.5 * ln(H/L)^2 - (2*ln(2) - 1) * ln(C/O)^2
    """
    log_hl = np.log(df["high"] / df["low"]) ** 2
    log_co = np.log(df["close"] / df["open"]) ** 2
    gk_bar = 0.5 * log_hl - (2.0 * np.log(2.0) - 1.0) * log_co
    gk_rolling = np.sqrt(gk_bar.rolling(window=period, min_periods=period).mean())
    return gk_rolling


def compute_volatility_features(
    df: pd.DataFrame,
    atr_period: int = 14,
    rolling_std_period: int = 20,
    bb_std_mult: float = 2.0,
) -> pd.DataFrame:
    """Computes standard volatility, range, and Bollinger Band features."""
    res = df.copy()
    close = res["close"]

    # Rolling return volatility (std of 1-bar log returns)
    log_ret = np.log(close / close.shift(1))
    res["feature_realized_vol_20b"] = log_ret.rolling(window=rolling_std_period, min_periods=rolling_std_period).std()

    # ATR
    atr = compute_atr(res, period=atr_period)
    res["feature_atr_14"] = atr
    res["feature_atr_pct"] = atr / close

    # Garman-Klass range volatility
    res["feature_garman_klass_vol"] = compute_garman_klass_volatility(res, period=rolling_std_period)

    # Bollinger Bands
    sma_bb = close.rolling(window=rolling_std_period, min_periods=rolling_std_period).mean()
    std_bb = close.rolling(window=rolling_std_period, min_periods=rolling_std_period).std()
    upper_bb = sma_bb + bb_std_mult * std_bb
    lower_bb = sma_bb - bb_std_mult * std_bb
    
    res["feature_bb_upper"] = upper_bb
    res["feature_bb_lower"] = lower_bb
    bb_width = upper_bb - lower_bb
    res["feature_bb_width"] = bb_width / sma_bb
    # Normalized position inside Bollinger Band: 0 = lower, 0.5 = mid, 1.0 = upper
    res["feature_bb_pct"] = (close - lower_bb) / (bb_width + 1e-10)

    return res
