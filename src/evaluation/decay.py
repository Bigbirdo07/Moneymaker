"""Signal decay curve analytics and predictive half-life estimation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class HorizonDecayMetric:
    """Realized forward performance at a specific holding horizon."""
    horizon_minutes: int
    horizon_bars: int
    sample_count: int
    mean_forward_return_bps: float
    median_forward_return_bps: float
    std_error_bps: float
    ci_lower_bps: float
    ci_upper_bps: float
    win_rate_pct: float
    annualized_sharpe_estimate: float


@dataclass
class SignalDecayReport:
    """Comprehensive decay profile across all horizons."""
    model_id: str
    peak_horizon_minutes: int
    peak_forward_return_bps: float
    half_life_minutes: float
    decay_curve: List[HorizonDecayMetric]


class SignalDecayAnalyzer:
    """Measures forward price trajectories and empirical half-life of candidate signals."""

    HORIZONS_MINUTES: List[int] = [5, 10, 15, 20, 30, 45, 60, 90, 120]

    @classmethod
    def compute_decay_curve(
        cls,
        df: pd.DataFrame,
        signals: List[any],
        model_id: str = "model",
    ) -> SignalDecayReport:
        """
        Calculates the mean forward return, median, standard error, and confidence intervals
        at each horizon following signal generation.
        """
        close = df["close"].values
        n = len(df)
        buy_indices = [i for i, s in enumerate(signals) if s.direction.value == "BUY"]

        if not buy_indices:
            return SignalDecayReport(
                model_id=model_id,
                peak_horizon_minutes=0,
                peak_forward_return_bps=0.0,
                half_life_minutes=0.0,
                decay_curve=[],
            )

        metrics: List[HorizonDecayMetric] = []
        for mins in cls.HORIZONS_MINUTES:
            bars = mins // 5
            rets = []
            for idx in buy_indices:
                if idx + bars < n:
                    r = (close[idx + bars] - close[idx]) / close[idx]
                    rets.append(r)

            if rets:
                rets_bps = np.array(rets) * 10000.0
                mean_bps = float(np.mean(rets_bps))
                med_bps = float(np.median(rets_bps))
                std_bps = float(np.std(rets_bps, ddof=1)) if len(rets) > 1 else 0.0
                se_bps = std_bps / np.sqrt(len(rets))
                win_r = float(np.mean(rets_bps > 0)) * 100.0
                sharpe_est = (mean_bps / (std_bps + 1e-8)) * np.sqrt(252.0 * (390.0 / mins))

                metrics.append(
                    HorizonDecayMetric(
                        horizon_minutes=mins,
                        horizon_bars=bars,
                        sample_count=len(rets),
                        mean_forward_return_bps=round(mean_bps, 2),
                        median_forward_return_bps=round(med_bps, 2),
                        std_error_bps=round(se_bps, 2),
                        ci_lower_bps=round(mean_bps - 1.96 * se_bps, 2),
                        ci_upper_bps=round(mean_bps + 1.96 * se_bps, 2),
                        win_rate_pct=round(win_r, 2),
                        annualized_sharpe_estimate=round(sharpe_est, 2),
                    )
                )

        # Determine peak horizon and half-life
        if metrics:
            peak_m = max(metrics, key=lambda m: m.mean_forward_return_bps)
            peak_min = peak_m.horizon_minutes
            peak_val = peak_m.mean_forward_return_bps

            # Half-life: first horizon after peak where return falls below peak / 2
            half_life = float(peak_min * 2.0)
            for m in metrics:
                if m.horizon_minutes > peak_min and m.mean_forward_return_bps <= (peak_val / 2.0):
                    half_life = float(m.horizon_minutes)
                    break
        else:
            peak_min = 0
            peak_val = 0.0
            half_life = 0.0

        return SignalDecayReport(
            model_id=model_id,
            peak_horizon_minutes=peak_min,
            peak_forward_return_bps=round(peak_val, 2),
            half_life_minutes=round(half_life, 1),
            decay_curve=metrics,
        )
