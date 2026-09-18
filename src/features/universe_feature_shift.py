"""
Cross-Sectional Feature Distribution Shift & PSI Evaluator (Phase B).
Measures Population Stability Index (PSI) and percentile stability
across universe scale expansions (50 -> 100 -> 250 -> 500 -> Full Liquid).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


def calculate_psi(expected: np.ndarray, actual: np.ndarray, num_buckets: int = 10) -> float:
    """
    Computes Population Stability Index (PSI) between baseline and scaled feature arrays.
    PSI < 0.10: No significant shift (Stable)
    0.10 <= PSI < 0.25: Moderate shift
    PSI >= 0.25: Significant shift / Domain shift detected
    """
    if len(expected) == 0 or len(actual) == 0:
        return 0.0

    # Determine quantiles on expected baseline
    quantiles = np.linspace(0, 100, num_buckets + 1)
    bucket_bounds = np.percentile(expected, quantiles)
    bucket_bounds[0] = -np.inf
    bucket_bounds[-1] = np.inf

    exp_counts, _ = np.histogram(expected, bins=bucket_bounds)
    act_counts, _ = np.histogram(actual, bins=bucket_bounds)

    exp_pct = np.maximum(exp_counts / len(expected), 1e-6)
    act_pct = np.maximum(act_counts / len(actual), 1e-6)

    psi = float(np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct)))
    return psi


def evaluate_feature_stability(
    df_fixed50: pd.DataFrame,
    df_expanded: pd.DataFrame,
    features: List[str],
) -> Dict[str, Any]:
    """Evaluates PSI across key cross-sectional ranking features."""
    results = {}
    for feat in features:
        if feat in df_fixed50.columns and feat in df_expanded.columns:
            v_fixed = df_fixed50[feat].dropna().values
            v_exp = df_expanded[feat].dropna().values
            psi_val = calculate_psi(v_fixed, v_exp)
            
            status = "STABLE" if psi_val < 0.10 else ("MODERATE_SHIFT" if psi_val < 0.25 else "DOMAIN_SHIFT")
            results[feat] = {
                "psi": round(psi_val, 4),
                "status": status,
                "mean_baseline": round(float(np.mean(v_fixed)), 4) if len(v_fixed) > 0 else 0.0,
                "mean_scaled": round(float(np.mean(v_exp)), 4) if len(v_exp) > 0 else 0.0,
            }
    return results
