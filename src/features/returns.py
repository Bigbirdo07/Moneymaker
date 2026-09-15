"""Multi-horizon return feature calculation, forward research targets, and economic labels."""

from __future__ import annotations

from typing import Dict, List, Optional
import numpy as np
import pandas as pd


def compute_return_features(df: pd.DataFrame, lookback_bars: List[int] = [1, 3, 6, 12]) -> pd.DataFrame:
    """Calculates backward-looking return features using strictly historical information."""
    res = df.copy()
    close = res["close"]
    new_cols: Dict[str, pd.Series] = {}
    for lb in lookback_bars:
        new_cols[f"feature_return_{lb}b"] = close.pct_change(lb)
        new_cols[f"feature_log_return_{lb}b"] = np.log(close / close.shift(lb))
    
    if new_cols:
        res = pd.concat([res, pd.DataFrame(new_cols, index=res.index)], axis=1)
    return res


def compute_target_returns(
    df: pd.DataFrame,
    forward_bars: List[int] = [1, 2, 3, 4, 6, 9, 12, 18, 24],  # 5m, 10m, 15m, 20m, 30m, 45m, 60m, 90m, 120m in 5m bars
    classification_thresholds_bps: List[float] = [5.0, 10.0, 15.0, 20.0],
    benchmark_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Computes multi-horizon forward return targets strictly for research evaluation.
    CRITICAL: Target columns MUST NEVER be used as training features or live trading inputs.
    """
    res = df.copy()
    close = res["close"]
    target_dict: Dict[str, np.ndarray | pd.Series] = {}

    for fwd in forward_bars:
        fwd_ret = (close.shift(-fwd) - close) / close
        mins = fwd * 5
        target_dict[f"target_future_return_{fwd}b"] = fwd_ret
        target_dict[f"target_return_{mins}m"] = fwd_ret

        for thresh_bps in classification_thresholds_bps:
            thresh_dec = thresh_bps / 10000.0
            thresh_str = f"{int(thresh_bps)}bps"
            
            target_dict[f"target_class_up_{mins}m_{thresh_str}"] = (fwd_ret >= thresh_dec).astype(int)
            target_dict[f"target_class_down_{mins}m_{thresh_str}"] = (fwd_ret <= -thresh_dec).astype(int)

            conds = [fwd_ret >= thresh_dec, fwd_ret <= -thresh_dec]
            choices = [1, -1]
            target_dict[f"target_class_3way_{mins}m_{thresh_str}"] = np.select(conds, choices, default=0)

    # Maintain backward compatibility with Phase 1 & 2 target names
    if 12 in forward_bars:
        ret_60m = (close.shift(-12) - close) / close
        target_dict["target_class_up_60m"] = (ret_60m >= 0.0010).astype(int) # 10 bps
        target_dict["target_class_down_60m"] = (ret_60m <= -0.0010).astype(int)
        conds = [ret_60m >= 0.0010, ret_60m <= -0.0010]
        target_dict["target_class_3way_60m"] = np.select(conds, [1, -1], default=0)

    # Market-adjusted relative forward returns if benchmark provided
    if benchmark_df is not None and not benchmark_df.empty:
        bench_close = benchmark_df.set_index("timestamp")["close"] if "timestamp" in benchmark_df.columns else benchmark_df["close"]
        asset_ts = pd.to_datetime(res["timestamp"], utc=True)
        aligned_bench = bench_close.reindex(asset_ts).values
        
        for fwd in forward_bars:
            mins = fwd * 5
            bench_fwd_ret = (pd.Series(aligned_bench).shift(-fwd) - pd.Series(aligned_bench)) / pd.Series(aligned_bench)
            fwd_ret = target_dict[f"target_return_{mins}m"]
            target_dict[f"target_market_adj_return_{mins}m"] = fwd_ret - bench_fwd_ret.values

    # Concatenate all targets at once to avoid fragmentation
    target_df = pd.DataFrame(target_dict, index=res.index)
    res = pd.concat([res, target_df], axis=1)
    return res
