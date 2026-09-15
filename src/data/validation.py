"""Data quality validation engine for market observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from src.data.schema import MarketDataSchema, REQUIRED_OHLCV_COLUMNS


@dataclass
class ValidationIssue:
    """Represents a specific data anomaly or validation failure."""
    category: str
    message: str
    row_count: int = 0
    sample_indices: List[int] = field(default_factory=list)


@dataclass
class DataValidationReport:
    """Comprehensive validation report for a dataset."""
    symbol: str
    is_valid: bool
    total_rows: int
    issues: List[ValidationIssue] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)

    def summary(self) -> str:
        status = "PASSED" if self.is_valid else "FAILED"
        issue_strs = [f" - [{iss.category}] {iss.message} (affected: {iss.row_count})" for iss in self.issues]
        issues_block = "\n".join(issue_strs) if issue_strs else " None"
        return (
            f"Validation Report for {self.symbol}: {status}\n"
            f"Total Bars: {self.total_rows}\n"
            f"Issues:\n{issues_block}"
        )


class DataValidator:
    """Validates raw and processed market time-series against financial and data-integrity rules."""

    def __init__(
        self,
        max_price_gap_pct: float = 0.20,  # 20% single-bar gap threshold
        expected_bar_interval: Optional[timedelta] = timedelta(minutes=5),
        allow_missing_bars: bool = True,  # Intraday bars can have gaps between sessions
    ) -> None:
        self.max_price_gap_pct = max_price_gap_pct
        self.expected_bar_interval = expected_bar_interval
        self.allow_missing_bars = allow_missing_bars

    def validate(self, df: pd.DataFrame, symbol: Optional[str] = None) -> DataValidationReport:
        """Runs the full validation suite on a market dataframe."""
        if df.empty:
            return DataValidationReport(
                symbol=symbol or "UNKNOWN",
                is_valid=False,
                total_rows=0,
                issues=[ValidationIssue(category="EMPTY_DATASET", message="DataFrame is completely empty", row_count=0)],
            )

        symbol_name = symbol or (str(df["symbol"].iloc[0]) if "symbol" in df.columns else "UNKNOWN")
        issues: List[ValidationIssue] = []

        # 1. Check required schema columns
        missing_cols = MarketDataSchema.validate_columns(df)
        if missing_cols:
            issues.append(
                ValidationIssue(
                    category="MISSING_COLUMNS",
                    message=f"Missing required columns: {missing_cols}",
                    row_count=len(missing_cols),
                )
            )
            return DataValidationReport(symbol=symbol_name, is_valid=False, total_rows=len(df), issues=issues)

        # Standardize types for validation
        clean_df = MarketDataSchema.enforce_types(df)

        # 2. Timezone & Null Timestamps
        null_ts = clean_df["timestamp"].isna()
        if null_ts.any():
            count = int(null_ts.sum())
            issues.append(
                ValidationIssue(
                    category="NULL_TIMESTAMPS",
                    message="Found null timestamps in dataset",
                    row_count=count,
                    sample_indices=clean_df.index[null_ts][:5].tolist(),
                )
            )

        # 3. Duplicate Timestamps
        duplicate_mask = clean_df.duplicated(subset=["timestamp"], keep=False)
        if duplicate_mask.any():
            count = int(duplicate_mask.sum())
            issues.append(
                ValidationIssue(
                    category="DUPLICATE_TIMESTAMPS",
                    message="Found duplicate timestamp rows",
                    row_count=count,
                    sample_indices=clean_df.index[duplicate_mask][:5].tolist(),
                )
            )

        # 4. Monotonicity / Out-of-order timestamps
        is_monotonic = clean_df["timestamp"].is_monotonic_increasing
        if not is_monotonic:
            diffs = clean_df["timestamp"].diff()
            out_of_order_mask = diffs < pd.Timedelta(0)
            count = int(out_of_order_mask.sum())
            issues.append(
                ValidationIssue(
                    category="OUT_OF_ORDER_TIMESTAMPS",
                    message="Timestamps are not strictly chronological",
                    row_count=count,
                    sample_indices=clean_df.index[out_of_order_mask][:5].tolist(),
                )
            )

        # 5. Impossible OHLC values
        # high >= low, high >= open, high >= close, low <= open, low <= close, all > 0
        neg_price_mask = (clean_df["open"] <= 0) | (clean_df["high"] <= 0) | (clean_df["low"] <= 0) | (clean_df["close"] <= 0)
        if neg_price_mask.any():
            count = int(neg_price_mask.sum())
            issues.append(
                ValidationIssue(
                    category="NON_POSITIVE_PRICES",
                    message="Found zero or negative prices",
                    row_count=count,
                    sample_indices=clean_df.index[neg_price_mask][:5].tolist(),
                )
            )

        high_low_violation = clean_df["high"] < clean_df["low"]
        if high_low_violation.any():
            count = int(high_low_violation.sum())
            issues.append(
                ValidationIssue(
                    category="IMPOSSIBLE_HIGH_LOW",
                    message="High is strictly less than Low",
                    row_count=count,
                    sample_indices=clean_df.index[high_low_violation][:5].tolist(),
                )
            )

        open_out_of_bounds = (clean_df["open"] > clean_df["high"]) | (clean_df["open"] < clean_df["low"])
        if open_out_of_bounds.any():
            count = int(open_out_of_bounds.sum())
            issues.append(
                ValidationIssue(
                    category="OPEN_OUT_OF_BOUNDS",
                    message="Open is outside [Low, High] bounds",
                    row_count=count,
                    sample_indices=clean_df.index[open_out_of_bounds][:5].tolist(),
                )
            )

        close_out_of_bounds = (clean_df["close"] > clean_df["high"]) | (clean_df["close"] < clean_df["low"])
        if close_out_of_bounds.any():
            count = int(close_out_of_bounds.sum())
            issues.append(
                ValidationIssue(
                    category="CLOSE_OUT_OF_BOUNDS",
                    message="Close is outside [Low, High] bounds",
                    row_count=count,
                    sample_indices=clean_df.index[close_out_of_bounds][:5].tolist(),
                )
            )

        # 6. Negative Volume
        neg_vol_mask = clean_df["volume"] < 0
        if neg_vol_mask.any():
            count = int(neg_vol_mask.sum())
            issues.append(
                ValidationIssue(
                    category="NEGATIVE_VOLUME",
                    message="Found negative volume observations",
                    row_count=count,
                    sample_indices=clean_df.index[neg_vol_mask][:5].tolist(),
                )
            )

        # 7. Unexplained extreme price jumps / gaps (> 20% single-bar jump)
        if len(clean_df) > 1:
            close_pct_change = clean_df["close"].pct_change().abs()
            extreme_gaps = close_pct_change > self.max_price_gap_pct
            if extreme_gaps.any():
                count = int(extreme_gaps.sum())
                issues.append(
                    ValidationIssue(
                        category="EXTREME_PRICE_GAP",
                        message=f"Found single-bar price returns exceeding {self.max_price_gap_pct:.1%}",
                        row_count=count,
                        sample_indices=clean_df.index[extreme_gaps][:5].tolist(),
                    )
                )

        # Dataset passes validation if there are no critical anomalies
        is_valid = len(issues) == 0

        metrics = {
            "row_count": float(len(clean_df)),
            "start_time": clean_df["timestamp"].min().timestamp() if not clean_df["timestamp"].isna().all() else 0.0,
            "end_time": clean_df["timestamp"].max().timestamp() if not clean_df["timestamp"].isna().all() else 0.0,
            "mean_close": float(clean_df["close"].mean()) if "close" in clean_df else 0.0,
            "mean_volume": float(clean_df["volume"].mean()) if "volume" in clean_df else 0.0,
        }

        return DataValidationReport(
            symbol=symbol_name,
            is_valid=is_valid,
            total_rows=len(clean_df),
            issues=issues,
            metrics=metrics,
        )
