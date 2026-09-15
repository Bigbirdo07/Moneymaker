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
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

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
        """
        Generates forward target returns across multi-day horizons.
        """
        df = daily_df.copy().sort_index()
        df["target_ret_1d"] = df["close"].shift(-1) / df["close"] - 1.0
        df["target_ret_2d"] = df["close"].shift(-2) / df["close"] - 1.0
        df["target_ret_3d"] = df["close"].shift(-3) / df["close"] - 1.0
        df["target_ret_5d"] = df["close"].shift(-5) / df["close"] - 1.0
        df["target_ret_10d"] = df["close"].shift(-10) / df["close"] - 1.0
        return df

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
