"""Feature and target contracts with runtime safety assertions against leakage."""

from __future__ import annotations

from typing import List, Set, Tuple
import pandas as pd

# Explicit prefixes and forbidden patterns
FORBIDDEN_PREFIXES: Tuple[str, ...] = (
    "target_",
    "future_",
    "forward_",
    "realized_future_",
    "post_trade_",
)

# Canonical allowable feature names
CANONICAL_FEATURES: List[str] = [
    "feature_return_1b",
    "feature_return_3b",
    "feature_return_6b",
    "feature_return_12b",
    "feature_log_return_1b",
    "feature_log_return_3b",
    "feature_log_return_6b",
    "feature_log_return_12b",
    "feature_rsi_14",
    "feature_macd_line",
    "feature_macd_signal",
    "feature_macd_hist",
    "feature_dist_ema_9",
    "feature_dist_ema_21",
    "feature_dist_ema_50",
    "feature_dist_sma_20",
    "feature_dist_sma_50",
    "feature_ema_cross_9_21",
    "feature_realized_vol_20b",
    "feature_atr_14",
    "feature_atr_pct",
    "feature_garman_klass_vol",
    "feature_bb_width",
    "feature_bb_pct",
    "feature_relative_volume_20b",
    "feature_volume_zscore_20b",
    "feature_volume_acceleration",
    "feature_vwap_deviation",
    "feature_price_volume_corr_5b",
    "feature_day_of_week",
    "feature_minutes_from_open",
    "feature_minutes_to_close",
    "feature_SPY_return_1b",
    "feature_SPY_return_6b",
    "feature_rel_strength_SPY_1b",
    "feature_rel_strength_SPY_6b",
]

TARGET_COLUMNS: List[str] = [
    "target_future_return_3b",
    "target_future_return_6b",
    "target_future_return_12b",
    "target_future_return_18b",
    "target_class_up_60m",
    "target_class_down_60m",
    "target_class_3way_60m",
]

METADATA_COLUMNS: List[str] = [
    "timestamp",
    "symbol",
    "event_timestamp",
    "available_timestamp",
]


class FeatureContractValidator:
    """Validates that matrices passed to ML models contain strictly permissible feature columns."""

    @staticmethod
    def get_feature_columns(df: pd.DataFrame, allowlist: List[str] | None = None) -> List[str]:
        """Extracts allowed feature column names from a DataFrame."""
        allowed = set(allowlist) if allowlist else set(CANONICAL_FEATURES)
        cols = [c for c in df.columns if c.startswith("feature_") and c in allowed]
        return cols

    @staticmethod
    def validate_features(columns: List[str] | pd.Index, allowlist: List[str] | None = None) -> List[str]:
        """
        Validates column names against forbidden leakage patterns and optional allowlist.
        Raises ValueError if any forbidden column is detected in the input list.
        Returns the validated list of feature column names.
        """
        cols = list(columns)
        forbidden_found = [c for c in cols if any(c.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)]
        if forbidden_found:
            raise ValueError(
                f"DATA LEAKAGE ATTEMPT DETECTED! Forbidden forward-looking columns present in feature matrix: {forbidden_found}"
            )

        allowed = set(allowlist) if allowlist else set(CANONICAL_FEATURES)
        valid_cols = [c for c in cols if c.startswith("feature_") and c in allowed]
        if not valid_cols:
            raise ValueError("No valid feature columns found in dataset matching the allowlist.")
        return valid_cols
