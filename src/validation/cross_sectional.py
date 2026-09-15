"""Cross-sectional generalization, sector-held-out validation, and leave-one-out sensitivity."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set
import numpy as np
import pandas as pd

from src.models.base import BaseMLModel
from src.strategies.ml_strategy import MLSignalStrategy
from src.backtest.engine import BacktestEngine, CompletedTrade
from src.backtest.costs import TransactionCostModel
from src.evaluation.metrics import MetricsCalculator, PerformanceSummary


@dataclass
class SectorHeldOutResult:
    """Evaluation metrics for a model trained on other sectors and tested on a held-out sector."""
    held_out_sector: str
    train_sectors: List[str]
    train_symbols: List[str]
    test_symbols: List[str]
    sample_count: int
    accuracy: float
    brier_score: float
    net_return_pct: float
    sharpe_ratio: float
    win_rate_pct: float
    total_trades: int


@dataclass
class ConcentrationReport:
    """Breakdown of return concentration across symbols and sectors."""
    top_1_symbol_pnl_pct: float
    top_5_symbols_pnl_pct: float
    top_sector_pnl_pct: float
    symbol_pnl_breakdown: Dict[str, float]
    sector_pnl_breakdown: Dict[str, float]
    is_concentrated: bool # True if top 1 symbol contributes > 50% of total profit


class CrossSectionalValidator:
    """Evaluates cross-sectional generalization across unseen securities, sectors, and time periods."""

    @staticmethod
    def evaluate_leave_sector_out(
        model_factory: Callable[[], BaseMLModel],
        universe_df: pd.DataFrame,
        sector_symbol_map: Dict[str, List[str]],
        feature_cols: List[str],
        target_col: str = "target_class_up_60m",
        cost_model: Optional[TransactionCostModel] = None,
    ) -> List[SectorHeldOutResult]:
        """
        Trains model on N-1 sectors and evaluates out-of-sample on the held-out sector.
        """
        results: List[SectorHeldOutResult] = []
        all_sectors = [s for s in sector_symbol_map.keys() if s != "broad_market_etfs"]
        calc = MetricsCalculator()
        backtester = BacktestEngine(initial_capital=1000.0, max_position_pct=0.10, cost_model=cost_model or TransactionCostModel())

        for held_out in all_sectors:
            test_syms = sector_symbol_map[held_out]
            train_sectors = [s for s in all_sectors if s != held_out]
            train_syms = [sym for s in train_sectors for sym in sector_symbol_map[s]]

            train_mask = universe_df["symbol"].isin(train_syms)
            test_mask = universe_df["symbol"].isin(test_syms)

            train_df = universe_df[train_mask].dropna(subset=feature_cols + [target_col])
            test_df = universe_df[test_mask].dropna(subset=feature_cols + [target_col])

            if len(train_df) < 50 or len(test_df) < 50:
                continue

            model = model_factory()
            model.fit(train_df[feature_cols], train_df[target_col])

            probs = model.predict_proba(test_df[feature_cols])
            preds = (probs[:, 1] >= 0.50).astype(int)

            y_test = test_df[target_col].values
            acc = float(np.mean(preds == y_test))
            brier = float(np.mean((probs[:, 1] - y_test) ** 2))

            # Run backtest on held-out sector
            strat = MLSignalStrategy(model=model, min_confidence=0.52)
            bt_res = backtester.run(strat, test_df)
            perf = calc.compute_summary(bt_res)

            results.append(
                SectorHeldOutResult(
                    held_out_sector=held_out,
                    train_sectors=train_sectors,
                    train_symbols=train_syms,
                    test_symbols=test_syms,
                    sample_count=len(test_df),
                    accuracy=round(acc, 4),
                    brier_score=round(brier, 4),
                    net_return_pct=perf.total_return_pct,
                    sharpe_ratio=perf.sharpe_ratio,
                    win_rate_pct=perf.win_rate_pct,
                    total_trades=perf.total_trades,
                )
            )
        return results

    @staticmethod
    def analyze_pnl_concentration(
        trades: List[CompletedTrade],
        symbol_to_sector_map: Optional[Dict[str, str]] = None,
    ) -> ConcentrationReport:
        """Measures P&L concentration by individual symbol and sector."""
        if not trades:
            return ConcentrationReport(
                top_1_symbol_pnl_pct=0.0,
                top_5_symbols_pnl_pct=0.0,
                top_sector_pnl_pct=0.0,
                symbol_pnl_breakdown={},
                sector_pnl_breakdown={},
                is_concentrated=False,
            )

        sym_pnl: Dict[str, float] = {}
        sec_pnl: Dict[str, float] = {}

        for t in trades:
            sym = t.symbol
            sym_pnl[sym] = sym_pnl.get(sym, 0.0) + t.net_pnl
            if symbol_to_sector_map:
                sec = symbol_to_sector_map.get(sym, "OTHER")
                sec_pnl[sec] = sec_pnl.get(sec, 0.0) + t.net_pnl

        tot_pnl = sum(sym_pnl.values())
        sorted_sym_pnl = sorted(sym_pnl.items(), key=lambda x: x[1], reverse=True)
        sorted_sec_pnl = sorted(sec_pnl.items(), key=lambda x: x[1], reverse=True)

        if tot_pnl > 0:
            top_1_pct = (sorted_sym_pnl[0][1] / tot_pnl) * 100.0 if sorted_sym_pnl else 0.0
            top_5_pnl = sum(v for _, v in sorted_sym_pnl[:5])
            top_5_pct = (top_5_pnl / tot_pnl) * 100.0 if sorted_sym_pnl else 0.0
            top_sec_pct = (sorted_sec_pnl[0][1] / tot_pnl) * 100.0 if sorted_sec_pnl else 0.0
        else:
            top_1_pct = 0.0
            top_5_pct = 0.0
            top_sec_pct = 0.0

        is_conc = top_1_pct > 50.0

        return ConcentrationReport(
            top_1_symbol_pnl_pct=round(top_1_pct, 2),
            top_5_symbols_pnl_pct=round(top_5_pct, 2),
            top_sector_pnl_pct=round(top_sec_pct, 2),
            symbol_pnl_breakdown={k: round(v, 4) for k, v in sym_pnl.items()},
            sector_pnl_breakdown={k: round(v, 4) for k, v in sec_pnl.items()},
            is_concentrated=is_conc,
        )

    @staticmethod
    def run_leave_one_symbol_out(
        backtester: BacktestEngine,
        strategy: MLSignalStrategy,
        universe_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Iteratively removes each symbol from the evaluation universe and measures performance impact.
        """
        symbols = universe_df["symbol"].unique().tolist()
        calc = MetricsCalculator()
        records = []

        # Baseline with all symbols
        all_res = backtester.run(strategy, universe_df)
        all_summary = calc.compute_summary(all_res)
        records.append({
            "excluded_symbol": "NONE (ALL)",
            "total_trades": all_summary.total_trades,
            "net_return_pct": all_summary.total_return_pct,
            "sharpe_ratio": all_summary.sharpe_ratio,
            "profit_factor": all_summary.profit_factor,
            "max_drawdown_pct": all_summary.max_drawdown_pct,
        })

        for sym in symbols:
            sub_df = universe_df[universe_df["symbol"] != sym].reset_index(drop=True)
            if sub_df.empty:
                continue
            sub_res = backtester.run(strategy, sub_df)
            sub_sum = calc.compute_summary(sub_res)
            records.append({
                "excluded_symbol": sym,
                "total_trades": sub_sum.total_trades,
                "net_return_pct": sub_sum.total_return_pct,
                "sharpe_ratio": sub_sum.sharpe_ratio,
                "profit_factor": sub_sum.profit_factor,
                "max_drawdown_pct": sub_sum.max_drawdown_pct,
            })

        return pd.DataFrame(records)
