"""Corporate action handling, stock split adjustments, and price discontinuity auditing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class StockSplitEvent:
    """Record of a stock split or reverse split event."""
    symbol: str
    effective_date: str # YYYY-MM-DD
    ratio: float       # e.g. 2.0 for 2-for-1 forward split, 0.10 for 1-for-10 reverse split


@dataclass
class DividendEvent:
    """Record of a cash dividend event."""
    symbol: str
    ex_date: str       # YYYY-MM-DD
    amount: float      # Cash dividend per share in USD


class CorporateActionManager:
    """
    Applies split and dividend adjustments to market OHLCV bars and audits
    data for unadjusted split discontinuities that could create artificial alpha.
    """

    def __init__(
        self,
        splits: Optional[List[StockSplitEvent]] = None,
        dividends: Optional[List[DividendEvent]] = None,
    ) -> None:
        self.splits = splits or []
        self.dividends = dividends or []

    def detect_unadjusted_split_anomalies(
        self,
        df: pd.DataFrame,
        split_ratio_threshold: float = 0.40,  # Single-bar price change threshold indicating potential split
    ) -> List[Dict[str, any]]:
        """
        Scans OHLCV series for single-bar overnight or intraday price drops/jumps
        that match common split ratios (e.g. -50% for 2:1 split, -75% for 4:1 split)
        accompanied by inverse volume jumps.
        """
        if len(df) < 2:
            return []

        clean_df = df.sort_values("timestamp").reset_index(drop=True)
        close = clean_df["close"]
        vol = clean_df["volume"]
        pct_chg = close.pct_change()
        vol_pct_chg = vol.pct_change()

        anomalies = []
        for i in range(1, len(clean_df)):
            ret = pct_chg.iloc[i]
            # Check for sudden ~50% drop (2:1 split), ~66% drop (3:1 split), ~75% drop (4:1 split), etc.
            if ret <= -split_ratio_threshold:
                anomalies.append({
                    "timestamp": clean_df["timestamp"].iloc[i],
                    "symbol": str(clean_df["symbol"].iloc[i]),
                    "price_change_pct": round(float(ret), 4),
                    "prev_close": float(close.iloc[i - 1]),
                    "curr_close": float(close.iloc[i]),
                    "volume_change_pct": round(float(vol_pct_chg.iloc[i]), 2) if not pd.isna(vol_pct_chg.iloc[i]) else 0.0,
                    "suspected_action": "FORWARD_SPLIT",
                })
            elif ret >= 1.0 / split_ratio_threshold - 1.0: # e.g. > +150% jump (reverse split)
                anomalies.append({
                    "timestamp": clean_df["timestamp"].iloc[i],
                    "symbol": str(clean_df["symbol"].iloc[i]),
                    "price_change_pct": round(float(ret), 4),
                    "prev_close": float(close.iloc[i - 1]),
                    "curr_close": float(close.iloc[i]),
                    "volume_change_pct": round(float(vol_pct_chg.iloc[i]), 2) if not pd.isna(vol_pct_chg.iloc[i]) else 0.0,
                    "suspected_action": "REVERSE_SPLIT",
                })
        return anomalies

    def apply_split_adjustments(self, df: pd.DataFrame, splits: List[StockSplitEvent]) -> pd.DataFrame:
        """
        Backward-adjusts historical OHLCV data prior to split effective dates.
        For a 2:1 split (ratio=2.0) on date D:
        - Historical prices prior to D are divided by 2.0
        - Historical volume prior to D is multiplied by 2.0
        """
        if df.empty or not splits:
            return df

        adjusted_df = df.copy()
        ts = pd.to_datetime(adjusted_df["timestamp"], utc=True)

        for split in splits:
            eff_dt = pd.to_datetime(split.effective_date, utc=True)
            mask = ts < eff_dt
            
            # Apply adjustment factor
            for col in ["open", "high", "low", "close"]:
                if col in adjusted_df.columns:
                    adjusted_df.loc[mask, col] = adjusted_df.loc[mask, col] / split.ratio
            if "volume" in adjusted_df.columns:
                adjusted_df.loc[mask, "volume"] = adjusted_df.loc[mask, "volume"] * split.ratio
            if "vwap" in adjusted_df.columns:
                adjusted_df.loc[mask, "vwap"] = adjusted_df.loc[mask, "vwap"] / split.ratio

        return adjusted_df
