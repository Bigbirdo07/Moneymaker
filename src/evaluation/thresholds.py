"""Validation threshold research and sensitivity analysis."""

from __future__ import annotations

from typing import List, Optional
import pandas as pd

from src.models.base import BaseMLModel
from src.models.calibration import ProbabilityCalibrator
from src.strategies.ml_strategy import MLSignalStrategy
from src.backtest.engine import BacktestEngine
from src.backtest.costs import TransactionCostModel
from src.evaluation.metrics import MetricsCalculator


class ThresholdResearcher:
    """Evaluates decision confidence thresholds exclusively on validation folds."""

    CANDIDATE_THRESHOLDS: List[float] = [0.50, 0.52, 0.55, 0.58, 0.60, 0.65, 0.70]

    @classmethod
    def evaluate_threshold_grid(
        cls,
        model: BaseMLModel,
        val_features_df: pd.DataFrame,
        calibrator: Optional[ProbabilityCalibrator] = None,
        cost_model: Optional[TransactionCostModel] = None,
        initial_capital: float = 1000.0,
    ) -> pd.DataFrame:
        """Runs backtests across candidate probability thresholds on validation data."""
        cost = cost_model or TransactionCostModel()
        backtester = BacktestEngine(initial_capital=initial_capital, max_position_pct=0.10, cost_model=cost)
        calc = MetricsCalculator()

        results = []
        for thresh in cls.CANDIDATE_THRESHOLDS:
            strat = MLSignalStrategy(
                model=model,
                calibrator=calibrator,
                min_confidence=thresh,
                min_expected_return_bps=5.0,
                name=f"ml_thresh_{thresh:.2f}",
            )
            res = backtester.run(strat, val_features_df)
            summary = calc.compute_summary(res)

            results.append({
                "threshold": thresh,
                "total_trades": summary.total_trades,
                "win_rate_pct": summary.win_rate_pct,
                "total_return_pct": summary.total_return_pct,
                "sharpe_ratio": summary.sharpe_ratio,
                "max_drawdown_pct": summary.max_drawdown_pct,
                "profit_factor": summary.profit_factor,
                "gross_pnl": summary.gross_pnl,
                "net_pnl": summary.net_pnl,
                "cost_drag": summary.total_friction_cost,
            })

        return pd.DataFrame(results)
