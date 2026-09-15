"""
Model Health Monitoring & Drift Detection for Phase 3A Shadow Validation.
Monitors operational health states (HEALTHY, WATCH, DEGRADED, SUSPENDED) and feature/prediction drift.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import numpy as np


class ModelHealthState(str, Enum):
    HEALTHY = "HEALTHY"
    WATCH = "WATCH"
    DEGRADED = "DEGRADED"
    SUSPENDED = "SUSPENDED"


@dataclass
class HealthStatusReport:
    state: ModelHealthState
    reason: str
    feature_drift_zscore: float
    prediction_mean: float
    stale_feed_count: int
    daily_lockout_active: bool
    recent_latency_ms: float


class ModelHealthMonitor:
    """Monitors incoming live distributions and health state triggers."""

    def __init__(
        self,
        historical_feature_means: Optional[Dict[str, float]] = None,
        historical_feature_stds: Optional[Dict[str, float]] = None,
        max_allowed_zscore: float = 3.5,
    ):
        self.feature_means = historical_feature_means or {
            "ret_15m": 0.0004,
            "volatility_14": 0.0035,
            "rvol_14": 1.15,
            "spread_bps": 2.2,
        }
        self.feature_stds = historical_feature_stds or {
            "ret_15m": 0.0040,
            "volatility_14": 0.0020,
            "rvol_14": 0.65,
            "spread_bps": 1.2,
        }
        self.max_allowed_zscore = max_allowed_zscore

    def evaluate_health(
        self,
        current_features: Dict[str, float],
        current_prediction: float,
        is_feed_valid: bool,
        is_daily_locked_out: bool,
        current_decision_latency_ms: float,
    ) -> HealthStatusReport:
        """Evaluate current system and model health status."""
        if not is_feed_valid:
            return HealthStatusReport(
                state=ModelHealthState.SUSPENDED,
                reason="FEED_DISCONNECTED_OR_STALE",
                feature_drift_zscore=0.0,
                prediction_mean=current_prediction,
                stale_feed_count=1,
                daily_lockout_active=is_daily_locked_out,
                recent_latency_ms=current_decision_latency_ms,
            )

        if is_daily_locked_out:
            return HealthStatusReport(
                state=ModelHealthState.SUSPENDED,
                reason="DAILY_RISK_LOCKOUT_ACTIVE",
                feature_drift_zscore=0.0,
                prediction_mean=current_prediction,
                stale_feed_count=0,
                daily_lockout_active=True,
                recent_latency_ms=current_decision_latency_ms,
            )

        # Check feature drift Z-scores
        max_z = 0.0
        drifted_feat = ""
        for feat, val in current_features.items():
            if feat in self.feature_means and feat in self.feature_stds:
                std = self.feature_stds[feat]
                if std > 0:
                    z = abs((val - self.feature_means[feat]) / std)
                    if z > max_z:
                        max_z = z
                        drifted_feat = feat

        if max_z > 4.5:
            return HealthStatusReport(
                state=ModelHealthState.DEGRADED,
                reason=f"EXTREME_FEATURE_DRIFT_{drifted_feat}_Z={max_z:.2f}",
                feature_drift_zscore=max_z,
                prediction_mean=current_prediction,
                stale_feed_count=0,
                daily_lockout_active=False,
                recent_latency_ms=current_decision_latency_ms,
            )

        if max_z > self.max_allowed_zscore or current_decision_latency_ms > 1500.0:
            return HealthStatusReport(
                state=ModelHealthState.WATCH,
                reason=f"ELEVATED_DRIFT_OR_LATENCY_Z={max_z:.2f}_LAT={current_decision_latency_ms:.0f}ms",
                feature_drift_zscore=max_z,
                prediction_mean=current_prediction,
                stale_feed_count=0,
                daily_lockout_active=False,
                recent_latency_ms=current_decision_latency_ms,
            )

        return HealthStatusReport(
            state=ModelHealthState.HEALTHY,
            reason="NORMAL",
            feature_drift_zscore=max_z,
            prediction_mean=current_prediction,
            stale_feed_count=0,
            daily_lockout_active=False,
            recent_latency_ms=current_decision_latency_ms,
        )
