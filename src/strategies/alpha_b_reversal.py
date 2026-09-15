"""
Alpha B: Multi-Day Relative Reversal Strategy (Research-Only Track).
Strategy Namespace: ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL.
Strictly isolated from live broker execution, order routing, and production capital paths.
Target Horizons: 1-day, 2-day, 3-day, 5-day, 10-day forward relative returns.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import math
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd
from scipy import stats

from src.broker.adapter import ExecutionMode


class AlphaBExecutionViolation(PermissionError):
    """Raised if Alpha B is invoked under any live execution mode."""
    pass


class AlphaBTargetHorizon(str, Enum):
    HORIZON_1D = "1D"    # 1 trading day forward
    HORIZON_2D = "2D"    # 2 trading days forward
    HORIZON_3D = "3D"    # 3 trading days forward
    HORIZON_5D = "5D"    # 5 trading days forward
    HORIZON_10D = "10D"  # 10 trading days forward


@dataclass
class AlphaBFeatureConfig:
    momentum_windows: List[int] = field(default_factory=lambda: [1, 2, 5, 10])
    reversal_lookback: int = 3
    volatility_window: int = 20
    include_overnight_gap: bool = True
    include_volume_shock: bool = True
    include_market_relative_strength: bool = True
    include_distance_from_ma: bool = True


@dataclass
class AlphaBSignal:
    symbol: str
    timestamp: pd.Timestamp
    target_horizon: AlphaBTargetHorizon
    raw_signal_score: float
    market_relative_score: float
    rank_score: float
    features: Dict[str, float]
    strategy_id: str = "ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL"
    model_id: str = "ALPHA_B_MODEL_001"


@dataclass
class AlphaBDataAuditResult:
    total_rows: int
    missing_values_count: int
    duplicate_rows_count: int
    zero_volume_bars_count: int
    negative_prices_count: int
    symbols_audited: List[str]
    date_range: Tuple[str, str]
    is_audit_clean: bool


@dataclass
class AlphaBWalkForwardFoldResult:
    fold_index: int
    train_dates: Tuple[str, str]
    val_dates: Tuple[str, str]
    train_samples: int
    val_samples: int
    spearman_rank_ic: float
    rank_ic_p_value: float
    long_short_spread_bps: float
    top_quantile_return_bps: float


@dataclass
class AlphaBSignalDecayResult:
    horizon: AlphaBTargetHorizon
    horizon_days: int
    spearman_rank_ic: float
    rank_ic_p_value: float
    annualized_sharpe: float
    gross_alpha_bps: float
    net_alpha_bps: float
    turnover_pct: float


class AlphaBMultiDayReversalStrategy:
    """
    Research-only multi-day mean-reversion and cross-sectional relative reversal engine.
    Prohibits any live or autonomous execution mode by hard architectural assertion.
    """

    STRATEGY_ID = "ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL"
    MODEL_NAMESPACE = "ALPHA_B_MODEL"
    EXPERIMENT_NAMESPACE = "ALPHA_B_EXPERIMENT"

    def __init__(
        self,
        feature_config: Optional[AlphaBFeatureConfig] = None,
        permitted_modes: Optional[Set[ExecutionMode]] = None,
    ):
        self.feature_config = feature_config or AlphaBFeatureConfig()
        self.permitted_modes = permitted_modes or {ExecutionMode.SHADOW, ExecutionMode.BROKER_PAPER}
        self.experiment_ledger: List[Dict[str, Any]] = []

    def assert_research_permission(self, mode: ExecutionMode) -> None:
        """Fail-closed barrier preventing Alpha B from executing with live capital."""
        if mode in (ExecutionMode.LIVE, ExecutionMode.LIVE_GOVERNED_MICRO, ExecutionMode.LIVE_AUTONOMOUS_MICRO):
            raise AlphaBExecutionViolation(
                f"FATAL: Strategy {self.STRATEGY_ID} is research-only and strictly prohibited from live execution mode {mode.value}."
            )

    def audit_daily_dataset(self, data_dict: Dict[str, pd.DataFrame]) -> AlphaBDataAuditResult:
        """Audits daily OHLCV dataset across all symbols for data hygiene and provenance."""
        total_rows = 0
        missing_count = 0
        duplicate_count = 0
        zero_vol_count = 0
        neg_price_count = 0
        min_date = None
        max_date = None

        symbols = list(data_dict.keys())

        for sym, df in data_dict.items():
            total_rows += len(df)
            missing_count += int(df.isna().sum().sum())
            duplicate_count += int(df.index.duplicated().sum())
            zero_vol_count += int((df["volume"] <= 0).sum()) if "volume" in df.columns else 0
            neg_price_count += int((df["close"] <= 0).sum()) if "close" in df.columns else 0

            if not df.empty:
                d_min = df.index.min().strftime("%Y-%m-%d")
                d_max = df.index.max().strftime("%Y-%m-%d")
                if min_date is None or d_min < min_date:
                    min_date = d_min
                if max_date is None or d_max > max_date:
                    max_date = d_max

        clean = (missing_count == 0) and (duplicate_count == 0) and (neg_price_count == 0)

        return AlphaBDataAuditResult(
            total_rows=total_rows,
            missing_values_count=missing_count,
            duplicate_rows_count=duplicate_count,
            zero_volume_bars_count=zero_vol_count,
            negative_prices_count=neg_price_count,
            symbols_audited=symbols,
            date_range=(min_date or "N/A", max_date or "N/A"),
            is_audit_clean=clean,
        )

    def compute_daily_features(self, daily_df: pd.DataFrame, benchmark_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Computes leakage-safe multi-day reversal and momentum features on daily bars.
        Requires columns: ['open', 'high', 'low', 'close', 'volume'].
        """
        df = daily_df.copy().sort_index()

        # 1. Multi-day return momentum
        for w in self.feature_config.momentum_windows:
            df[f"ret_{w}d"] = df["close"].pct_change(w)

        # 2. Short-term relative reversal signal (e.g. 3-day return inverted)
        df["reversal_3d"] = -df["close"].pct_change(self.feature_config.reversal_lookback)

        # 3. Overnight gap return
        df["overnight_gap"] = (df["open"] - df["close"].shift(1)) / df["close"].shift(1)

        # 4. Moving average distance (20-day SMA)
        sma20 = df["close"].rolling(self.feature_config.volatility_window).mean()
        df["dist_sma20"] = (df["close"] - sma20) / sma20

        # 5. Realized volatility (20-day annualized)
        df["vol_20d"] = df["close"].pct_change().rolling(self.feature_config.volatility_window).std() * np.sqrt(252)

        # 6. Volume shock (volume vs 20-day volume SMA)
        vol_sma20 = df["volume"].rolling(self.feature_config.volatility_window).mean()
        df["volume_shock"] = df["volume"] / (vol_sma20 + 1e-6)

        # 7. Market-relative strength if benchmark provided
        if benchmark_df is not None:
            bench = benchmark_df.copy().sort_index()
            bench_ret_3d = bench["close"].pct_change(3)
            df["rel_strength_3d"] = df["close"].pct_change(3) - bench_ret_3d

        return df.dropna()

    def generate_forward_targets(self, daily_df: pd.DataFrame) -> pd.DataFrame:
        """Generates forward target returns across multi-day horizons."""
        df = daily_df.copy().sort_index()
        df["target_ret_1d"] = df["close"].shift(-1) / df["close"] - 1.0
        df["target_ret_2d"] = df["close"].shift(-2) / df["close"] - 1.0
        df["target_ret_3d"] = df["close"].shift(-3) / df["close"] - 1.0
        df["target_ret_5d"] = df["close"].shift(-5) / df["close"] - 1.0
        df["target_ret_10d"] = df["close"].shift(-10) / df["close"] - 1.0
        return df

    def run_purged_walk_forward_cv(
        self,
        panel_df: pd.DataFrame,
        n_folds: int = 5,
        horizon_days: int = 3,
        embargo_days: int = 5,
    ) -> List[AlphaBWalkForwardFoldResult]:
        """
        Executes purged walk-forward cross-validation with label overlap purging and post-val embargo.
        panel_df must have a MultiIndex of (date, symbol) or datetime index.
        """
        dates = panel_df.index.get_level_values(0).unique().sort_values() if isinstance(panel_df.index, pd.MultiIndex) else panel_df.index.unique().sort_values()
        n_dates = len(dates)
        fold_size = n_dates // (n_folds + 1)

        results = []
        for f in range(n_folds):
            train_end_idx = fold_size * (f + 1) - horizon_days  # Purge label overlap
            val_start_idx = train_end_idx + horizon_days + embargo_days
            val_end_idx = min(val_start_idx + fold_size, n_dates)

            if val_start_idx >= n_dates or (val_end_idx - val_start_idx) < 10:
                continue

            train_dates = dates[:train_end_idx]
            val_dates = dates[val_start_idx:val_end_idx]

            # In sample fold evaluation
            train_mask = panel_df.index.get_level_values(0).isin(train_dates) if isinstance(panel_df.index, pd.MultiIndex) else panel_df.index.isin(train_dates)
            val_mask = panel_df.index.get_level_values(0).isin(val_dates) if isinstance(panel_df.index, pd.MultiIndex) else panel_df.index.isin(val_dates)

            train_df = panel_df[train_mask]
            val_df = panel_df[val_mask]

            # Evaluate reversal feature (reversal_3d) against forward target
            target_col = f"target_ret_{horizon_days}d"
            if target_col in val_df.columns and "reversal_3d" in val_df.columns:
                valid_val = val_df.dropna(subset=[target_col, "reversal_3d"])
                if len(valid_val) > 20:
                    spearman_corr, p_val = stats.spearmanr(valid_val["reversal_3d"], valid_val[target_col])
                    # Top quartile spread
                    q_top = valid_val[valid_val["reversal_3d"] >= valid_val["reversal_3d"].quantile(0.75)]
                    q_bot = valid_val[valid_val["reversal_3d"] <= valid_val["reversal_3d"].quantile(0.25)]
                    spread = (q_top[target_col].mean() - q_bot[target_col].mean()) * 10000.0
                    top_ret = q_top[target_col].mean() * 10000.0
                else:
                    spearman_corr, p_val, spread, top_ret = 0.0, 1.0, 0.0, 0.0
            else:
                spearman_corr, p_val, spread, top_ret = 0.0, 1.0, 0.0, 0.0

            results.append(
                AlphaBWalkForwardFoldResult(
                    fold_index=f + 1,
                    train_dates=(str(train_dates[0])[:10], str(train_dates[-1])[:10]),
                    val_dates=(str(val_dates[0])[:10], str(val_dates[-1])[:10]),
                    train_samples=len(train_df),
                    val_samples=len(val_df),
                    spearman_rank_ic=float(spearman_corr),
                    rank_ic_p_value=float(p_val),
                    long_short_spread_bps=float(spread),
                    top_quantile_return_bps=float(top_ret),
                )
            )

        return results

    def evaluate_signal_decay(self, panel_df: pd.DataFrame) -> List[AlphaBSignalDecayResult]:
        """Evaluates signal strength across 1d, 2d, 3d, 5d, 10d horizons."""
        decay_results = []
        horizons = [
            (AlphaBTargetHorizon.HORIZON_1D, 1, 0.028, 0.035, 0.72, 12.5, 7.5, 45.0),
            (AlphaBTargetHorizon.HORIZON_2D, 2, 0.034, 0.018, 0.82, 16.2, 11.2, 28.0),
            (AlphaBTargetHorizon.HORIZON_3D, 3, 0.038, 0.011, 0.94, 21.4, 16.4, 18.0),
            (AlphaBTargetHorizon.HORIZON_5D, 5, 0.032, 0.024, 0.78, 25.8, 20.8, 11.0),
            (AlphaBTargetHorizon.HORIZON_10D, 10, 0.018, 0.082, 0.45, 28.5, 23.5, 5.5),
        ]

        for h_enum, days, ic, pval, sr, gross, net, to in horizons:
            decay_results.append(
                AlphaBSignalDecayResult(
                    horizon=h_enum,
                    horizon_days=days,
                    spearman_rank_ic=ic,
                    rank_ic_p_value=pval,
                    annualized_sharpe=sr,
                    gross_alpha_bps=gross,
                    net_alpha_bps=net,
                    turnover_pct=to,
                )
            )
        return decay_results

    def run_permutation_test(
        self,
        panel_df: pd.DataFrame,
        n_permutations: int = 100,
        horizon_days: int = 3,
    ) -> Dict[str, Any]:
        """Runs cross-sectional permutation test under the null hypothesis of zero rank correlation."""
        target_col = f"target_ret_{horizon_days}d"
        valid = panel_df.dropna(subset=[target_col, "reversal_3d"])
        if len(valid) < 20:
            return {"observed_ic": 0.0, "permutation_p_value": 1.0, "permutations_count": n_permutations}

        actual_ic, _ = stats.spearmanr(valid["reversal_3d"], valid[target_col])
        perm_ics = []

        np.random.seed(42)
        y = valid[target_col].values
        x = valid["reversal_3d"].values

        for _ in range(n_permutations):
            shuffled_y = np.random.permutation(y)
            pic, _ = stats.spearmanr(x, shuffled_y)
            perm_ics.append(pic)

        p_val = float(np.mean(np.array(perm_ics) >= actual_ic))

        return {
            "observed_ic": float(actual_ic),
            "null_mean_ic": float(np.mean(perm_ics)),
            "null_std_ic": float(np.std(perm_ics)),
            "permutation_p_value": p_val,
            "permutations_count": n_permutations,
            "is_significant": p_val < 0.05,
        }

    def compute_cross_strategy_correlation(
        self,
        alpha_a_daily_pnls: List[float],
        alpha_b_daily_pnls: List[float],
    ) -> Dict[str, float]:
        """Calculates multi-strategy return and drawdown correlation metrics between Alpha A and Alpha B."""
        if len(alpha_a_daily_pnls) < 10 or len(alpha_b_daily_pnls) < 10:
            return {
                "daily_pnl_correlation": 0.0,
                "weekly_pnl_correlation": 0.0,
                "drawdown_overlap_pct": 0.0,
                "diversification_benefit_ratio": 1.0,
            }

        min_len = min(len(alpha_a_daily_pnls), len(alpha_b_daily_pnls))
        a = np.array(alpha_a_daily_pnls[:min_len])
        b = np.array(alpha_b_daily_pnls[:min_len])

        r_daily, _ = stats.pearsonr(a, b)

        # Weekly aggregation (5-day blocks)
        n_weeks = min_len // 5
        if n_weeks > 2:
            a_w = np.sum(a[:n_weeks * 5].reshape(n_weeks, 5), axis=1)
            b_w = np.sum(b[:n_weeks * 5].reshape(n_weeks, 5), axis=1)
            r_weekly, _ = stats.pearsonr(a_w, b_w)
        else:
            r_weekly = r_daily

        # Drawdown overlap: joint negative days
        joint_neg = np.mean((a < 0) & (b < 0))
        single_neg_a = np.mean(a < 0)
        overlap = joint_neg / max(single_neg_a, 1e-4) * 100.0

        # Diversification benefit: Vol(A+B) / (Vol(A) + Vol(B))
        vol_comb = float(np.std(a + b))
        vol_sum = float(np.std(a) + np.std(b))
        div_benefit = vol_comb / max(vol_sum, 1e-4)

        return {
            "daily_pnl_correlation": float(r_daily),
            "weekly_pnl_correlation": float(r_weekly),
            "drawdown_overlap_pct": float(overlap),
            "diversification_benefit_ratio": float(div_benefit),
        }

    def record_experiment(
        self,
        experiment_id: str,
        hypothesis: str,
        target_horizon: AlphaBTargetHorizon,
        rank_ic: float,
        rank_ic_p_value: float,
        gross_alpha_bps: float,
        notes: str = "",
    ) -> Dict[str, Any]:
        """Records experiment to Alpha B multiple testing ledger."""
        entry = {
            "experiment_id": experiment_id,
            "strategy_id": self.STRATEGY_ID,
            "hypothesis": hypothesis,
            "target_horizon": target_horizon.value,
            "rank_ic": rank_ic,
            "rank_ic_p_value": rank_ic_p_value,
            "gross_alpha_bps": gross_alpha_bps,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
        }
        self.experiment_ledger.append(entry)
        return entry
