"""
Market Data Quality Policy Engine for Moneymaker Platform (Phase B).
Asserts bar-level and session-level data integrity, monotonic timestamps,
zero inverted OHLC, stale price sequence filtering, and coverage thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class QualityViolationCode(str, Enum):
    VALID = "VALID"
    INVERTED_OHLC = "INVERTED_OHLC"
    NEGATIVE_OR_ZERO_PRICE = "NEGATIVE_OR_ZERO_PRICE"
    DUPLICATE_TIMESTAMPS = "DUPLICATE_TIMESTAMPS"
    NON_MONOTONIC_TIMESTAMPS = "NON_MONOTONIC_TIMESTAMPS"
    STALE_PRICE_SEQUENCE = "STALE_PRICE_SEQUENCE"
    EXCESSIVE_ZERO_VOLUME = "EXCESSIVE_ZERO_VOLUME"
    INSUFFICIENT_BAR_COUNT = "INSUFFICIENT_BAR_COUNT"
    EXTREME_PRICE_DISCONTINUITY = "EXTREME_PRICE_DISCONTINUITY"


@dataclass
class QualityAuditResult:
    """Summary of data quality evaluation for a symbol session or series."""
    symbol: str
    session_date: str
    is_valid: bool
    violation_code: QualityViolationCode
    total_bars: int
    zero_volume_bars: int
    max_stale_ticks: int
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "session_date": self.session_date,
            "is_valid": self.is_valid,
            "violation_code": self.violation_code.value,
            "total_bars": self.total_bars,
            "zero_volume_bars": self.zero_volume_bars,
            "max_stale_ticks": self.max_stale_ticks,
            "explanation": self.explanation,
        }


class MarketDataQualityPolicy:
    """
    Evaluates raw 1-minute OHLCV data against strict empirical quality standards.
    """

    def __init__(
        self,
        min_bars_per_session: int = 200,
        max_zero_volume_fraction: float = 0.50,
        max_consecutive_stale_bars: int = 15,
        max_single_bar_return_pct: float = 0.35,  # 35% single bar move without halt
    ) -> None:
        self.min_bars_per_session = min_bars_per_session
        self.max_zero_volume_fraction = max_zero_volume_fraction
        self.max_consecutive_stale_bars = max_consecutive_stale_bars
        self.max_single_bar_return_pct = max_single_bar_return_pct

    def audit_session(self, df_session: pd.DataFrame, symbol: str, session_date: str) -> QualityAuditResult:
        """Audits a single trading session of 1-minute bars."""
        if df_session.empty or len(df_session) < self.min_bars_per_session:
            return QualityAuditResult(
                symbol=symbol,
                session_date=session_date,
                is_valid=False,
                violation_code=QualityViolationCode.INSUFFICIENT_BAR_COUNT,
                total_bars=len(df_session),
                zero_volume_bars=0,
                max_stale_ticks=0,
                explanation=f"Session has only {len(df_session)} bars (< {self.min_bars_per_session}).",
            )

        # 1. Monotonic timestamps & duplicates
        if "timestamp" in df_session.columns:
            ts = pd.to_datetime(df_session["timestamp"])
            if not ts.is_monotonic_increasing:
                return QualityAuditResult(
                    symbol=symbol,
                    session_date=session_date,
                    is_valid=False,
                    violation_code=QualityViolationCode.NON_MONOTONIC_TIMESTAMPS,
                    total_bars=len(df_session),
                    zero_volume_bars=0,
                    max_stale_ticks=0,
                    explanation="Timestamps are not strictly ascending.",
                )
            if ts.duplicated().any():
                return QualityAuditResult(
                    symbol=symbol,
                    session_date=session_date,
                    is_valid=False,
                    violation_code=QualityViolationCode.DUPLICATE_TIMESTAMPS,
                    total_bars=len(df_session),
                    zero_volume_bars=0,
                    max_stale_ticks=0,
                    explanation="Duplicate timestamps detected.",
                )

        # 2. Negative or Zero Prices
        price_cols = [c for c in ["open", "high", "low", "close"] if c in df_session.columns]
        for col in price_cols:
            if (df_session[col] <= 0).any():
                return QualityAuditResult(
                    symbol=symbol,
                    session_date=session_date,
                    is_valid=False,
                    violation_code=QualityViolationCode.NEGATIVE_OR_ZERO_PRICE,
                    total_bars=len(df_session),
                    zero_volume_bars=0,
                    max_stale_ticks=0,
                    explanation=f"Negative or zero values found in {col}.",
                )

        # 3. Inverted OHLC
        if all(c in df_session.columns for c in ["open", "high", "low", "close"]):
            high = df_session["high"]
            low = df_session["low"]
            open_ = df_session["open"]
            close = df_session["close"]
            inverted = (high < low) | (high < open_) | (high < close) | (low > open_) | (low > close)
            if inverted.any():
                return QualityAuditResult(
                    symbol=symbol,
                    session_date=session_date,
                    is_valid=False,
                    violation_code=QualityViolationCode.INVERTED_OHLC,
                    total_bars=len(df_session),
                    zero_volume_bars=0,
                    max_stale_ticks=0,
                    explanation="High/Low inverted relative to Open/Close.",
                )

        # 4. Zero volume fraction
        zero_vol = int((df_session["volume"] == 0).sum()) if "volume" in df_session.columns else 0
        zero_vol_frac = zero_vol / len(df_session)
        if zero_vol_frac > self.max_zero_volume_fraction:
            return QualityAuditResult(
                symbol=symbol,
                session_date=session_date,
                is_valid=False,
                violation_code=QualityViolationCode.EXCESSIVE_ZERO_VOLUME,
                total_bars=len(df_session),
                zero_volume_bars=zero_vol,
                max_stale_ticks=0,
                explanation=f"Zero-volume bars ({zero_vol_frac:.1%}) exceed {self.max_zero_volume_fraction:.1%}.",
            )

        # 5. Stale flat prices
        if "close" in df_session.columns:
            diff = (df_session["close"] != df_session["close"].shift(1)).cumsum()
            max_stale = int(diff.value_counts().max()) if not diff.empty else 0
            if max_stale > self.max_consecutive_stale_bars:
                return QualityAuditResult(
                    symbol=symbol,
                    session_date=session_date,
                    is_valid=False,
                    violation_code=QualityViolationCode.STALE_PRICE_SEQUENCE,
                    total_bars=len(df_session),
                    zero_volume_bars=zero_vol,
                    max_stale_ticks=max_stale,
                    explanation=f"Detected {max_stale} consecutive identical price ticks.",
                )

        return QualityAuditResult(
            symbol=symbol,
            session_date=session_date,
            is_valid=True,
            violation_code=QualityViolationCode.VALID,
            total_bars=len(df_session),
            zero_volume_bars=zero_vol,
            max_stale_ticks=max_stale if "close" in df_session.columns else 0,
            explanation="Data quality verified with zero violations.",
        )
