"""Stress testing suite: cost sensitivity, execution delays, signal decay, and feature ablation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
import numpy as np
import pandas as pd

from src.models.base import BaseMLModel
from src.strategies.ml_strategy import MLSignalStrategy
from src.backtest.engine import BacktestEngine
from src.backtest.costs import TransactionCostModel
from src.evaluation.metrics import MetricsCalculator


@dataclass
class CostStressResult:
    """Outcome of strategy under scaled transaction friction."""
    cost_multiplier: float
    effective_spread_bps: float
    effective_slippage_bps: float
    net_return_pct: float
    sharpe_ratio: float
    profit_factor: float
    total_friction_drag: float
    is_profitable: bool


@dataclass
class ExecutionDelayResult:
    """Outcome of strategy when order fills are subjected to latency/delays."""
    delay_bars: int
    delay_minutes: int
    net_return_pct: float
    sharpe_ratio: float
    win_rate_pct: float
    total_trades: int


class StrategyStressTester:
    """Stress testing suite for quantitative alpha strategies."""

    @staticmethod
    def run_cost_sensitivity_stress_test(
        strategy: MLSignalStrategy,
        df: pd.DataFrame,
        base_half_spread_bps: float = 1.5,
        base_slippage_bps: float = 2.0,
        multipliers: List[float] = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0],
    ) -> tuple[List[CostStressResult], float]:
        """
        Tests performance across scaled transaction costs and computes the break-even friction threshold in bps.
        """
        results: List[CostStressResult] = []
        calc = MetricsCalculator()

        for mult in multipliers:
            eff_spread = base_half_spread_bps * mult
            eff_slip = base_slippage_bps * mult
            cost_mod = TransactionCostModel(half_spread_bps=eff_spread, base_slippage_bps=eff_slip)
            backtester = BacktestEngine(initial_capital=1000.0, max_position_pct=0.10, cost_model=cost_mod)

            res = backtester.run(strategy, df)
            summary = calc.compute_summary(res)

            results.append(
                CostStressResult(
                    cost_multiplier=mult,
                    effective_spread_bps=eff_spread,
                    effective_slippage_bps=eff_slip,
                    net_return_pct=summary.total_return_pct,
                    sharpe_ratio=summary.sharpe_ratio,
                    profit_factor=summary.profit_factor,
                    total_friction_drag=summary.total_friction_cost,
                    is_profitable=summary.total_return_pct > 0.0,
                )
            )

        # Calculate break-even friction in bps by linear interpolation
        # Cost = total friction bps (spread + slippage)
        # Find where net_return_pct drops below 0
        break_even_bps = 0.0
        for i in range(len(results) - 1):
            r1, r2 = results[i], results[i + 1]
            if r1.net_return_pct >= 0.0 and r2.net_return_pct < 0.0:
                slope = (r2.net_return_pct - r1.net_return_pct)
                f1_bps = r1.effective_spread_bps + r1.effective_slippage_bps
                f2_bps = r2.effective_spread_bps + r2.effective_slippage_bps
                if abs(slope) > 1e-6:
                    break_even_bps = f1_bps + (-r1.net_return_pct / slope) * (f2_bps - f1_bps)
                break
            elif r1.net_return_pct > 0.0 and r2.net_return_pct >= 0.0:
                break_even_bps = r2.effective_spread_bps + r2.effective_slippage_bps

        return results, round(break_even_bps, 2)

    @staticmethod
    def run_execution_delay_test(
        model: BaseMLModel,
        df: pd.DataFrame,
        delays: List[int] = [0, 1, 2], # 0, 1 bar (5m), 2 bars (10m)
        cost_model: Optional[TransactionCostModel] = None,
    ) -> List[ExecutionDelayResult]:
        """
        Simulates latency by shifting strategy signals forward by N bars before execution.
        """
        results: List[ExecutionDelayResult] = []
        cost = cost_model or TransactionCostModel()
        calc = MetricsCalculator()

        for delay in delays:
            strat = MLSignalStrategy(model=model, min_confidence=0.52)
            clean_df = df.copy()
            backtester = BacktestEngine(initial_capital=1000.0, max_position_pct=0.10, cost_model=cost)

            # Generate original signals
            orig_signals = strat.generate_signals(clean_df)
            
            # If delay > 0, shift signal direction by delay bars
            if delay > 0:
                shifted_signals = []
                for i in range(len(orig_signals)):
                    if i >= delay:
                        source_sig = orig_signals[i - delay]
                        shifted_sig = orig_signals[i]
                        shifted_sig.direction = source_sig.direction
                        shifted_sig.signal_strength = source_sig.signal_strength
                        shifted_sig.confidence = source_sig.confidence
                    else:
                        shifted_signals.append(orig_signals[i])
            
            bt_res = backtester.run(strat, clean_df)
            summary = calc.compute_summary(bt_res)

            results.append(
                ExecutionDelayResult(
                    delay_bars=delay,
                    delay_minutes=delay * 5,
                    net_return_pct=summary.total_return_pct,
                    sharpe_ratio=summary.sharpe_ratio,
                    win_rate_pct=summary.win_rate_pct,
                    total_trades=summary.total_trades,
                )
            )

        return results

    @staticmethod
    def analyze_signal_decay(
        df: pd.DataFrame,
        signals: List[any],
        forward_horizons_bars: List[int] = [1, 3, 6, 12, 18, 24], # 5m, 15m, 30m, 60m, 90m, 120m
    ) -> pd.DataFrame:
        """
        Measures the forward return trajectory of high-confidence signals over time.
        """
        close = df["close"].values
        n = len(df)
        decay_records = []

        buy_indices = [i for i, s in enumerate(signals) if s.direction.value == "BUY"]
        if not buy_indices:
            return pd.DataFrame()

        for fwd in forward_horizons_bars:
            returns_at_fwd = []
            for idx in buy_indices:
                if idx + fwd < n:
                    ret = (close[idx + fwd] - close[idx]) / close[idx]
                    returns_at_fwd.append(ret)

            if returns_at_fwd:
                decay_records.append({
                    "horizon_bars": fwd,
                    "horizon_minutes": fwd * 5,
                    "mean_forward_return_bps": round(float(np.mean(returns_at_fwd)) * 10000.0, 2),
                    "win_rate_pct": round(float(np.mean(np.array(returns_at_fwd) > 0)) * 100.0, 2),
                    "sample_count": len(returns_at_fwd),
                })

        return pd.DataFrame(decay_records)

    @staticmethod
    def run_feature_ablation(
        model_factory: Callable[[], BaseMLModel],
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        feature_families: Dict[str, List[str]],
        target_col: str = "target_class_up_60m",
    ) -> pd.DataFrame:
        """
        Removes one feature family at a time to measure drop in test ROC-AUC and accuracy.
        """
        all_features = [f for fam in feature_families.values() for f in fam if f in train_df.columns]
        
        # Baseline with all features
        m_base = model_factory()
        m_base.fit(train_df[all_features], train_df[target_col])
        base_probs = m_base.predict_proba(test_df[all_features])[:, 1]
        y_test = test_df[target_col].values
        base_roc = float(np.nan_to_num(np.mean(base_probs == y_test))) # fallback metric

        records = [{
            "ablated_family": "NONE (ALL FEATURES)",
            "features_used_count": len(all_features),
            "test_accuracy": round(float(np.mean((base_probs >= 0.5) == y_test)), 4),
            "test_brier": round(float(np.mean((base_probs - y_test) ** 2)), 4),
        }]

        for fam_name, fam_cols in feature_families.items():
            ablated_feats = [f for f in all_features if f not in fam_cols]
            if not ablated_feats:
                continue

            m = model_factory()
            m.fit(train_df[ablated_feats], train_df[target_col])
            probs = m.predict_proba(test_df[ablated_feats])[:, 1]
            acc = float(np.mean((probs >= 0.5) == y_test))
            brier = float(np.mean((probs - y_test) ** 2))

            records.append({
                "ablated_family": f"EXCLUDE_{fam_name.upper()}",
                "features_used_count": len(ablated_feats),
                "test_accuracy": round(acc, 4),
                "test_brier": round(brier, 4),
            })

        return pd.DataFrame(records)
