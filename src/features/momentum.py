"""Momentum and trend technical features calculated with zero lookahead bias."""

from __future__ import annotations

from typing import List, Optional
import numpy as np
import pandas as pd


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculates Wilder's Relative Strength Index (RSI)."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder's exponential smoothing
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def compute_macd(
    series: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculates MACD line, Signal line, and MACD Histogram."""
    ema_fast = series.ewm(span=fast_period, adjust=False).mean()
    ema_slow = series.ewm(span=slow_period, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    macd_hist = macd_line - signal_line
    return macd_line, signal_line, macd_hist


def compute_momentum_features(
    df: pd.DataFrame,
    rsi_period: int = 14,
    ema_periods: List[int] = [9, 21, 50],
    sma_periods: List[int] = [20, 50],
) -> pd.DataFrame:
    """Computes all momentum, trend, and oscillator features."""
    res = df.copy()
    close = res["close"]

    # RSI
    res["feature_rsi_14"] = compute_rsi(close, period=rsi_period)

    # MACD
    macd, signal, hist = compute_macd(close, 12, 26, 9)
    res["feature_macd_line"] = macd / close  # Normalized by price
    res["feature_macd_signal"] = signal / close
    res["feature_macd_hist"] = hist / close

    # EMAs and distances
    for span in ema_periods:
        ema = close.ewm(span=span, adjust=False).mean()
        res[f"feature_ema_{span}"] = ema
        res[f"feature_dist_ema_{span}"] = (close - ema) / ema

    # SMAs and distances
    for span in sma_periods:
        sma = close.rolling(window=span, min_periods=span).mean()
        res[f"feature_sma_{span}"] = sma
        res[f"feature_dist_sma_{span}"] = (close - sma) / sma

    # EMA cross / short vs medium momentum
    if 9 in ema_periods and 21 in ema_periods:
        res["feature_ema_cross_9_21"] = (res["feature_ema_9"] - res["feature_ema_21"]) / res["feature_ema_21"]

    return res
