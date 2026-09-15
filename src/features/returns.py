"""Return feature calculation and future research target generation."""

from __future__ import annotations

from typing import List
import numpy as np
import pandas as pd


def compute_return_features(df: pd.DataFrame, lookback_bars: List[int] = [1, 3, 6, 12]) -> pd.DataFrame:
    """Calculates backward-looking return features using only strictly historical information."""
    res = df.copy()
    close = res["close"]
    for lb in lookback_bars:
        # Simple percentage return over lb bars
        res[f"feature_return_{lb}b"] = close.pct_change(lb)
        # Log return
        res[f"feature_log_return_{lb}b"] = np.log(close / close.shift(lb))
    return res


def compute_target_returns(
    df: pd.DataFrame,
    forward_bars: List[int] = [3, 6, 12, 18],  # 15m, 30m, 60m, 90m in 5m bars
    classification_threshold: float = 0.005,    # 0.50%
) -> pd.DataFrame:
    """
    Computes forward return targets for statistical and ML model training/evaluation.
    CRITICAL: Target columns MUST NEVER be used as training features or live trading inputs.
    """
    res = df.copy()
    close = res["close"]
    
    for fwd in forward_bars:
        # Forward return: (close(t+fwd) - close(t)) / close(t)
        fwd_ret = (close.shift(-fwd) - close) / close
        res[f"target_future_return_{fwd}b"] = fwd_ret

    # Default 60-minute target classification (12 bars * 5m = 60m)
    if 12 in forward_bars:
        ret_60m = res["target_future_return_12b"]
        res["target_class_up_60m"] = (ret_60m > classification_threshold).astype(int)
        res["target_class_down_60m"] = (ret_60m < -classification_threshold).astype(int)
        
        # 3-class target: 1 = UP, 0 = FLAT, -1 = DOWN
        conditions = [
            ret_60m > classification_threshold,
            ret_60m < -classification_threshold,
        ]
        choices = [1, -1]
        res["target_class_3way_60m"] = np.select(conditions, choices, default=0)

    return res
