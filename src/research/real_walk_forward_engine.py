"""
Real Walk-Forward Multi-Regime Engine for Phase 11A.
Executes rolling-origin out-of-sample evaluations of frozen Real Market Engine V2
across 12 independent monthly windows in 2025.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from src.core.logging import get_logger
from src.core.types import EvidenceClass
from src.features.real_market_feature_store import RealMarketFeatureStore
from src.models.real_market_multi_horizon_forecaster_v2 import RealMarketMultiHorizonForecasterV2
from src.signals.real_market_entry_model_v2 import RealMarketEntryModelV2
from src.signals.real_market_exit_model_v2 import RealMarketExitModelV2
from src.execution.real_market_allocator_v2 import RealMarketAllocatorV2
from src.replay.real_engine_v2_runner import RealEngineV2Runner, RealTradeV2Record

logger = get_logger("research.real_walk_forward_engine")

SECTOR_MAP = {
    'AAPL': 'Technology', 'MSFT': 'Technology', 'NVDA': 'Technology', 'AVGO': 'Technology',
    'ORCL': 'Technology', 'CRM': 'Technology', 'CSCO': 'Technology', 'ACN': 'Technology',
    'ADBE': 'Technology', 'INTC': 'Technology', 'AMD': 'Technology', 'TXN': 'Technology',
    'QCOM': 'Technology', 'AMZN': 'Consumer Cyclical', 'TSLA': 'Consumer Cyclical',
    'HD': 'Consumer Cyclical', 'MCD': 'Consumer Cyclical', 'NKE': 'Consumer Cyclical',
    'LOW': 'Consumer Cyclical', 'GOOGL': 'Communication Services', 'META': 'Communication Services',
    'NFLX': 'Communication Services', 'CMCSA': 'Communication Services', 'DIS': 'Communication Services',
    'BRK.B': 'Financials', 'JPM': 'Financials', 'V': 'Financials', 'MA': 'Financials',
    'BAC': 'Financials', 'WFC': 'Financials', 'MS': 'Financials', 'GS': 'Financials',
    'LLY': 'Healthcare', 'JNJ': 'Healthcare', 'UNH': 'Healthcare', 'ABBV': 'Healthcare',
    'MRK': 'Healthcare', 'TMO': 'Healthcare', 'ABT': 'Healthcare', 'PFE': 'Healthcare',
    'WMT': 'Consumer Defensive', 'PG': 'Consumer Defensive', 'COST': 'Consumer Defensive',
    'KO': 'Consumer Defensive', 'PEP': 'Consumer Defensive', 'XOM': 'Energy', 'CVX': 'Energy',
    'LIN': 'Basic Materials', 'CAT': 'Industrials', 'GE': 'Industrials'
}


class RealWalkForwardEngine:
    """
    Executes rigorous expanding-origin walk-forward validation across real historical market regimes.
    """

    def __init__(
        self,
        data_dir: str = "data/processed/alpaca_extended_1m",
        artifact_dir: str = "artifacts/unity/phase11a",
        initial_capital: float = 1000.0,
    ) -> None:
        self.data_dir = data_dir
        self.artifact_dir = Path(artifact_dir)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.initial_capital = initial_capital
        self.feature_store = RealMarketFeatureStore(data_dir=data_dir)

    def _load_or_build_master_matrix(self) -> pd.DataFrame:
        """Loads cached 2024-2025 matrix if available, or constructs from parquet files."""
        cached_path = Path("data/processed/matrix_cache/matrix_2024-01-02_2025-12-31_step15.parquet")
        if cached_path.exists():
            logger.info("Loading precomputed 2024–2025 feature matrix from %s...", cached_path)
            return pd.read_parquet(cached_path)

        logger.info("Extracting full 2024–2025 feature matrix from %s...", self.data_dir)
        dfs = []
        p_dir = Path(self.data_dir)
        files = sorted(list(p_dir.glob("*_1m.parquet")))
        for f in files:
            sym = f.name.replace("_1m.parquet", "")
            try:
                raw_df = self.feature_store.load_symbol_dataframe(sym)
                sub_df = raw_df[(raw_df["date_str"] >= "2024-01-02") & (raw_df["date_str"] <= "2025-12-31")]
                if len(sub_df) > 50:
                    feat_df = self.feature_store.compute_symbol_features_vectorized(sym, sub_df, sample_step=15)
                    if not feat_df.empty:
                        dfs.append(feat_df)
            except Exception as e:
                logger.warning("Error processing symbol %s: %s", sym, e)

        full_df = pd.concat(dfs, ignore_index=True)
        if "timestamp_et" in full_df.columns:
            full_df["cs_ret_15m_rank"] = full_df.groupby("timestamp_et")["ret_15m_bps"].rank(pct=True).fillna(0.5)
            full_df["cs_ret_60m_rank"] = full_df.groupby("timestamp_et")["ret_60m_bps"].rank(pct=True).fillna(0.5)
            full_df["cs_volume_rank"] = full_df.groupby("timestamp_et")["relative_volume"].rank(pct=True).fillna(0.5)
        return full_df

    def run_walk_forward_study(
        self,
        windows: List[Dict[str, str]],
        experiment_id: str,
    ) -> Dict[str, Any]:
        """
        Runs the complete rolling walk-forward evaluation across all specified monthly windows.
        """
        logger.info("Initiating Phase 11A Walk-Forward Study across %d windows...", len(windows))
        master_matrix = self._load_or_build_master_matrix()
        symbols = sorted(master_matrix["symbol"].unique().tolist())
        logger.info("Master matrix loaded: %d observations across %d symbols.", len(master_matrix), len(symbols))

        all_monthly_results = []
        all_trades_list = []
        current_capital = self.initial_capital

        for w_idx, win in enumerate(windows, 1):
            month_id = win["month_id"]
            train_start, train_end = win["train_start"], win["train_end"]
            eval_start, eval_end = win["eval_start"], win["eval_end"]

            logger.info(
                "[Window %d/%d] %s | Train: %s to %s | Eval: %s to %s",
                w_idx, len(windows), month_id, train_start, train_end, eval_start, eval_end
            )

            # 1. Slicing training matrix strictly up to train_end
            train_df = master_matrix[(master_matrix["date_str"] >= train_start) & (master_matrix["date_str"] <= train_end)]
            logger.info("Train matrix size: %d rows", len(train_df))

            # 2. Fit Forecaster V2 strictly on prior data
            forecaster = RealMarketMultiHorizonForecasterV2()
            forecaster.train(train_df)

            # 3. Slicing evaluation matrix for month T
            eval_df = master_matrix[(master_matrix["date_str"] >= eval_start) & (master_matrix["date_str"] <= eval_end)]
            logger.info("Eval matrix size for %s: %d rows", month_id, len(eval_df))

            # 4. Compute Broad Signal Diagnostics for Month T
            signal_diag = self._compute_signal_diagnostics(eval_df, forecaster)

            # 5. Execute Replay on Month T with Frozen Runner
            entry_model = RealMarketEntryModelV2(min_net_edge_bps=12.0, min_calibrated_prob=0.55, max_daily_trades=3)
            exit_model = RealMarketExitModelV2(stop_loss_pct=0.015, take_profit_pct=0.03, trailing_drawdown_pct=0.008, max_holding_bars=90)
            allocator = RealMarketAllocatorV2(max_active_positions=2, sizing_policy="VOLATILITY_ADJUSTED", max_position_capital_pct=0.5)

            runner = RealEngineV2Runner(
                forecaster=forecaster,
                entry_model=entry_model,
                exit_model=exit_model,
                allocator=allocator,
                feature_store=self.feature_store,
                starting_capital=current_capital,
                symbols=symbols,
            )

            replay_res = runner.run_replay(
                features_df=eval_df,
                start_date=eval_start,
                end_date=eval_end,
                cost_multiplier=1.0,
            )

            trades = replay_res.get("trades", [])
            trade_dicts = [t.to_dict() for t in trades]
            trades_df = pd.DataFrame(trade_dicts) if trade_dicts else pd.DataFrame()

            if not trades_df.empty:
                trades_df["month_id"] = month_id
                trades_df["sector"] = trades_df["symbol"].map(SECTOR_MAP).fillna("Other")
                all_trades_list.append(trades_df)

            # 6. Analyze Month Metrics
            month_metrics = self._analyze_monthly_window(
                month_id=month_id,
                win=win,
                replay_res=replay_res,
                trades_df=trades_df,
                eval_df=eval_df,
                signal_diag=signal_diag,
                starting_capital=current_capital,
            )

            all_monthly_results.append(month_metrics)

            # Update capital for compounding tracking
            current_capital = month_metrics["ending_capital"]

        # Concatenate all executed trades
        all_trades_df = pd.concat(all_trades_list, ignore_index=True) if all_trades_list else pd.DataFrame()

        # Save monthly parquet ledger
        if not all_trades_df.empty:
            parquet_path = self.artifact_dir / "PHASE_11A_MONTHLY_RESULTS.parquet"
            all_trades_df.to_parquet(parquet_path)
            logger.info("Saved all walk-forward trades to %s (%d total trades)", parquet_path, len(all_trades_df))

        # 7. Aggregate Multi-Month Analysis
        aggregate_metrics = self._compute_aggregate_study_metrics(
            monthly_results=all_monthly_results,
            all_trades_df=all_trades_df,
            initial_capital=self.initial_capital,
        )

        return {
            "experiment_id": experiment_id,
            "windows_count": len(windows),
            "monthly_results": all_monthly_results,
            "aggregate_metrics": aggregate_metrics,
        }

    def _compute_signal_diagnostics(
        self,
        eval_df: pd.DataFrame,
        forecaster: RealMarketMultiHorizonForecasterV2,
    ) -> Dict[str, float]:
        """Computes broad cross-sectional ICs for the evaluation month."""
        try:
            feats = forecaster.FEATURE_COLS
            x_eval = eval_df[feats].fillna(0.0).values
            preds_15m = forecaster.regressors[15].predict(x_eval)
            preds_30m = forecaster.regressors[30].predict(x_eval)
            preds_60m = forecaster.regressors[60].predict(x_eval)
            composite_pred = (preds_15m + preds_30m + preds_60m) / 3.0

            ic_15m = float(stats.spearmanr(preds_15m, eval_df["fwd_raw_15m_bps"].fillna(0.0)).correlation) if len(eval_df) > 10 else 0.0
            ic_30m = float(stats.spearmanr(preds_30m, eval_df["fwd_raw_30m_bps"].fillna(0.0)).correlation) if len(eval_df) > 10 else 0.0
            ic_60m = float(stats.spearmanr(preds_60m, eval_df["fwd_raw_60m_bps"].fillna(0.0)).correlation) if len(eval_df) > 10 else 0.0
            ic_comp = float(stats.spearmanr(composite_pred, eval_df["fwd_raw_60m_bps"].fillna(0.0)).correlation) if len(eval_df) > 10 else 0.0

            pm_mask = (eval_df["overnight_gap_bps"].abs() > 20.0) if "overnight_gap_bps" in eval_df.columns else pd.Series(False, index=eval_df.index)
            if pm_mask.sum() > 30:
                ic_pm = float(stats.spearmanr(composite_pred[pm_mask], eval_df.loc[pm_mask, "fwd_raw_60m_bps"].fillna(0.0)).correlation)
            else:
                ic_pm = 0.0

            return {
                "rank_ic_15m": round(float(np.nan_to_num(ic_15m)), 4),
                "rank_ic_30m": round(float(np.nan_to_num(ic_30m)), 4),
                "rank_ic_60m": round(float(np.nan_to_num(ic_60m)), 4),
                "broad_composite_ic": round(float(np.nan_to_num(ic_comp)), 4),
                "premarket_drift_ic": round(float(np.nan_to_num(ic_pm)), 4),
            }
        except Exception as e:
            logger.warning("Signal diagnostics warning: %s", str(e))
            return {
                "rank_ic_15m": 0.0,
                "rank_ic_30m": 0.0,
                "rank_ic_60m": 0.0,
                "broad_composite_ic": 0.0,
                "premarket_drift_ic": 0.0,
            }

    def _analyze_monthly_window(
        self,
        month_id: str,
        win: Dict[str, str],
        replay_res: Any,
        trades_df: pd.DataFrame,
        eval_df: pd.DataFrame,
        signal_diag: Dict[str, float],
        starting_capital: float,
    ) -> Dict[str, Any]:
        """Analyzes performance, concentration, regimes, and horizons for a single month."""
        unique_sessions = eval_df["date_str"].nunique() if "date_str" in eval_df.columns else 21
        n_trades = len(trades_df)

        if n_trades == 0:
            return {
                "month_id": month_id,
                "starting_capital": starting_capital,
                "ending_capital": starting_capital,
                "net_return_pct": 0.0,
                "gross_return_pct": 0.0,
                "net_pnl": 0.0,
                "gross_pnl": 0.0,
                "total_friction": 0.0,
                "trade_count": 0,
                "trades_per_day": 0.0,
                "sessions_count": unique_sessions,
                "zero_trade_days": unique_sessions,
                "one_trade_days": 0,
                "two_trade_days": 0,
                "three_plus_trade_days": 0,
                "win_rate_pct": 0.0,
                "profit_factor": 0.0,
                "payoff_ratio": 0.0,
                "expectancy_per_trade_dlr": 0.0,
                "max_drawdown_pct": 0.0,
                "best_symbol": "NONE",
                "best_symbol_pct": 0.0,
                "top_3_symbols_pct": 0.0,
                "best_day": "NONE",
                "best_day_pct": 0.0,
                "top_3_days_pct": 0.0,
                "top_3_trades_pct": 0.0,
                "top_10_trades_pct": 0.0,
                "counterfactual_ex_best_trade_pnl": 0.0,
                "counterfactual_ex_best_day_pnl": 0.0,
                "counterfactual_ex_best_symbol_pnl": 0.0,
                "cost_stress": {
                    "cost_1_0x_pnl": 0.0,
                    "cost_1_5x_pnl": 0.0,
                    "cost_2_0x_pnl": 0.0,
                    "cost_3_0x_pnl": 0.0,
                },
                "signal_diagnostics": signal_diag,
            }

        net_pnl = float(trades_df["net_pnl"].sum())
        gross_pnl = float(trades_df["gross_pnl"].sum())
        total_friction = float(trades_df["total_friction"].sum())
        net_ret_pct = round((net_pnl / starting_capital) * 100.0, 2)
        gross_ret_pct = round((gross_pnl / starting_capital) * 100.0, 2)
        ending_capital = starting_capital + net_pnl

        wins = trades_df[trades_df["net_pnl"] > 0]
        losses = trades_df[trades_df["net_pnl"] < 0]
        n_wins = len(wins)
        n_losses = len(losses)
        win_rate = round((n_wins / n_trades) * 100.0, 2)
        gw = wins["net_pnl"].sum()
        gl = abs(losses["net_pnl"].sum())
        pf = round(gw / gl, 2) if gl > 0 else (99.0 if gw > 0 else 0.0)

        avg_w = float(wins["net_pnl"].mean()) if n_wins > 0 else 0.0
        avg_l = abs(float(losses["net_pnl"].mean())) if n_losses > 0 else 0.0
        payoff = round(avg_w / avg_l, 2) if avg_l > 0 else 0.0
        exp_trade = round(net_pnl / n_trades, 2)

        # Selectivity pacing
        trades_per_day = round(n_trades / max(1, unique_sessions), 2)
        day_counts = trades_df.groupby("session_date")["trade_id"].count()
        zero_trade_days = unique_sessions - len(day_counts)
        one_trade_days = int((day_counts == 1).sum())
        two_trade_days = int((day_counts == 2).sum())
        three_plus_trade_days = int((day_counts >= 3).sum())

        # Concentration metrics
        sym_pnl = trades_df.groupby("symbol")["net_pnl"].sum().sort_values(ascending=False)
        best_sym = sym_pnl.index[0] if len(sym_pnl) > 0 else "NONE"
        best_sym_pnl = float(sym_pnl.iloc[0]) if len(sym_pnl) > 0 else 0.0
        top3_sym_pnl = float(sym_pnl.iloc[:3].sum()) if len(sym_pnl) >= 3 else float(sym_pnl.sum())

        day_pnl = trades_df.groupby("session_date")["net_pnl"].sum().sort_values(ascending=False)
        best_day = day_pnl.index[0] if len(day_pnl) > 0 else "NONE"
        best_day_pnl = float(day_pnl.iloc[0]) if len(day_pnl) > 0 else 0.0
        top3_day_pnl = float(day_pnl.iloc[:3].sum()) if len(day_pnl) >= 3 else float(day_pnl.sum())

        sorted_trades = trades_df.sort_values(by="net_pnl", ascending=False)
        best_trade_pnl = float(sorted_trades["net_pnl"].iloc[0]) if n_trades > 0 else 0.0
        top3_trades_pnl = float(sorted_trades["net_pnl"].iloc[:3].sum()) if n_trades >= 3 else float(sorted_trades["net_pnl"].sum())
        top10_trades_pnl = float(sorted_trades["net_pnl"].iloc[:10].sum()) if n_trades >= 10 else float(sorted_trades["net_pnl"].sum())

        denom = abs(net_pnl) if abs(net_pnl) > 0.01 else 1.0
        best_sym_pct = round((best_sym_pnl / denom) * 100.0, 2)
        top3_sym_pct = round((top3_sym_pnl / denom) * 100.0, 2)
        best_day_pct = round((best_day_pnl / denom) * 100.0, 2)
        top3_day_pct = round((top3_day_pnl / denom) * 100.0, 2)
        top3_trades_pct = round((top3_trades_pnl / denom) * 100.0, 2)
        top10_trades_pct = round((top10_trades_pnl / denom) * 100.0, 2)

        ex_best_trade_pnl = round(net_pnl - best_trade_pnl, 2)
        ex_best_day_pnl = round(net_pnl - best_day_pnl, 2)
        ex_best_sym_pnl = round(net_pnl - best_sym_pnl, 2)

        cum_pnl = trades_df["net_pnl"].cumsum()
        equity_curve = starting_capital + cum_pnl
        running_peak = np.maximum.accumulate(equity_curve)
        drawdowns = (running_peak - equity_curve) / running_peak * 100.0
        max_dd = round(float(drawdowns.max()), 2) if len(drawdowns) > 0 else 0.0

        cost_1_5x_pnl = round(gross_pnl - (total_friction * 1.5), 2)
        cost_2_0x_pnl = round(gross_pnl - (total_friction * 2.0), 2)
        cost_3_0x_pnl = round(gross_pnl - (total_friction * 3.0), 2)

        return {
            "month_id": month_id,
            "starting_capital": starting_capital,
            "ending_capital": ending_capital,
            "net_return_pct": net_ret_pct,
            "gross_return_pct": gross_ret_pct,
            "net_pnl": round(net_pnl, 2),
            "gross_pnl": round(gross_pnl, 2),
            "total_friction": round(total_friction, 2),
            "trade_count": n_trades,
            "trades_per_day": trades_per_day,
            "sessions_count": unique_sessions,
            "zero_trade_days": zero_trade_days,
            "one_trade_days": one_trade_days,
            "two_trade_days": two_trade_days,
            "three_plus_trade_days": three_plus_trade_days,
            "win_rate_pct": win_rate,
            "profit_factor": pf,
            "payoff_ratio": payoff,
            "expectancy_per_trade_dlr": exp_trade,
            "max_drawdown_pct": max_dd,
            "avg_bars_held": round(float(trades_df["bars_held"].mean()), 1),
            "median_bars_held": round(float(trades_df["bars_held"].median()), 1),
            "best_symbol": best_sym,
            "best_symbol_pct": best_sym_pct,
            "top_3_symbols_pct": top3_sym_pct,
            "best_day": best_day,
            "best_day_pct": best_day_pct,
            "top_3_days_pct": top3_day_pct,
            "top_3_trades_pct": top3_trades_pct,
            "top_10_trades_pct": top10_trades_pct,
            "counterfactual_ex_best_trade_pnl": ex_best_trade_pnl,
            "counterfactual_ex_best_day_pnl": ex_best_day_pnl,
            "counterfactual_ex_best_symbol_pnl": ex_best_sym_pnl,
            "cost_stress": {
                "cost_1_0x_pnl": round(net_pnl, 2),
                "cost_1_5x_pnl": cost_1_5x_pnl,
                "cost_2_0x_pnl": cost_2_0x_pnl,
                "cost_3_0x_pnl": cost_3_0x_pnl,
            },
            "signal_diagnostics": signal_diag,
        }

    def _compute_aggregate_study_metrics(
        self,
        monthly_results: List[Dict[str, Any]],
        all_trades_df: pd.DataFrame,
        initial_capital: float,
    ) -> Dict[str, Any]:
        """Computes aggregate multi-month study statistics and bootstrap bounds."""
        n_months = len(monthly_results)
        monthly_returns = [m["net_return_pct"] for m in monthly_results]
        monthly_pnls = [m["net_pnl"] for m in monthly_results]
        profitable_months = sum(1 for p in monthly_pnls if p > 0)
        losing_months = sum(1 for p in monthly_pnls if p < 0)
        pct_profitable_months = round((profitable_months / max(1, n_months)) * 100.0, 1)

        total_net_pnl = sum(monthly_pnls)
        total_gross_pnl = sum(m["gross_pnl"] for m in monthly_results)
        total_friction = sum(m["total_friction"] for m in monthly_results)
        compounded_capital = monthly_results[-1]["ending_capital"] if monthly_results else initial_capital
        compounded_return_pct = round(((compounded_capital - initial_capital) / initial_capital) * 100.0, 2)

        total_trades = len(all_trades_df)
        all_wins = all_trades_df[all_trades_df["net_pnl"] > 0] if not all_trades_df.empty else pd.DataFrame()
        all_losses = all_trades_df[all_trades_df["net_pnl"] < 0] if not all_trades_df.empty else pd.DataFrame()
        overall_win_rate = round((len(all_wins) / max(1, total_trades)) * 100.0, 2)

        gw = all_wins["net_pnl"].sum() if not all_wins.empty else 0.0
        gl = abs(all_losses["net_pnl"].sum()) if not all_losses.empty else 0.0
        overall_pf = round(gw / gl, 2) if gl > 0 else 0.0
        overall_expectancy = round(total_net_pnl / max(1, total_trades), 2)

        if not all_trades_df.empty:
            agg_sym_pnl = all_trades_df.groupby("symbol")["net_pnl"].sum().sort_values(ascending=False)
            best_agg_sym = agg_sym_pnl.index[0]
            best_agg_sym_pnl = float(agg_sym_pnl.iloc[0])
            top3_agg_sym_pnl = float(agg_sym_pnl.iloc[:3].sum())
            top3_sym_pct = round((top3_agg_sym_pnl / max(0.01, abs(total_net_pnl))) * 100.0, 1)

            sorted_agg_trades = all_trades_df.sort_values(by="net_pnl", ascending=False)
            top3_agg_trades_pnl = float(sorted_agg_trades["net_pnl"].iloc[:3].sum())
            top3_trades_pct = round((top3_agg_trades_pnl / max(0.01, abs(total_net_pnl))) * 100.0, 1)
            top10_agg_trades_pnl = float(sorted_agg_trades["net_pnl"].iloc[:10].sum())
            top10_trades_pct = round((top10_agg_trades_pnl / max(0.01, abs(total_net_pnl))) * 100.0, 1)

            agg_ex_best_trade_pnl = round(total_net_pnl - float(sorted_agg_trades["net_pnl"].iloc[0]), 2)
            agg_ex_top3_trades_pnl = round(total_net_pnl - top3_agg_trades_pnl, 2)
            agg_ex_best_sym_pnl = round(total_net_pnl - best_agg_sym_pnl, 2)
        else:
            best_agg_sym = "NONE"
            top3_sym_pct = 0.0
            top3_trades_pct = 0.0
            top10_trades_pct = 0.0
            agg_ex_best_trade_pnl = 0.0
            agg_ex_top3_trades_pnl = 0.0
            agg_ex_best_sym_pnl = 0.0

        profitable_1_0x = sum(1 for m in monthly_results if m["cost_stress"]["cost_1_0x_pnl"] > 0)
        profitable_1_5x = sum(1 for m in monthly_results if m["cost_stress"]["cost_1_5x_pnl"] > 0)
        profitable_2_0x = sum(1 for m in monthly_results if m["cost_stress"]["cost_2_0x_pnl"] > 0)
        profitable_3_0x = sum(1 for m in monthly_results if m["cost_stress"]["cost_3_0x_pnl"] > 0)
        agg_breakeven_mult = round(total_gross_pnl / max(0.01, total_friction), 2)

        # Bootstrap Uncertainty (10,000 resamples)
        if not all_trades_df.empty and total_trades > 10:
            trade_pnls = all_trades_df["net_pnl"].values
            boot_pnls = []
            boot_exps = []
            np.random.seed(42)
            for _ in range(10_000):
                sample = np.random.choice(trade_pnls, size=len(trade_pnls), replace=True)
                boot_pnls.append(sample.sum())
                boot_exps.append(sample.mean())

            pnl_ci = [round(float(np.percentile(boot_pnls, 2.5)), 2), round(float(np.percentile(boot_pnls, 97.5)), 2)]
            exp_ci = [round(float(np.percentile(boot_exps, 2.5)), 2), round(float(np.percentile(boot_exps, 97.5)), 2)]
        else:
            pnl_ci = [0.0, 0.0]
            exp_ci = [0.0, 0.0]

        # Determine Formal Verdicts
        if pct_profitable_months >= 70.0 and overall_pf >= 1.25 and total_net_pnl > 0:
            val_verdict = "BROADER_VALIDATION_POSITIVE"
        elif pct_profitable_months >= 50.0 and total_net_pnl > 0:
            val_verdict = "BROADER_VALIDATION_MIXED"
        else:
            val_verdict = "BROADER_VALIDATION_FAILED"

        if top3_trades_pct > 75.0 or top3_sym_pct > 60.0:
            conc_verdict = "CONCENTRATION_STRUCTURAL"
        elif top3_trades_pct > 50.0:
            conc_verdict = "CONCENTRATION_REGIME_SPECIFIC"
        else:
            conc_verdict = "CONCENTRATION_ACCEPTABLE"

        return {
            "total_evaluated_months": n_months,
            "profitable_months_count": profitable_months,
            "losing_months_count": losing_months,
            "pct_profitable_months": pct_profitable_months,
            "median_monthly_return_pct": round(float(np.median(monthly_returns)), 2) if monthly_returns else 0.0,
            "mean_monthly_return_pct": round(float(np.mean(monthly_returns)), 2) if monthly_returns else 0.0,
            "best_month_return_pct": max(monthly_returns) if monthly_returns else 0.0,
            "worst_month_return_pct": min(monthly_returns) if monthly_returns else 0.0,
            "compounded_capital": round(compounded_capital, 2),
            "compounded_return_pct": compounded_return_pct,
            "total_net_pnl": round(total_net_pnl, 2),
            "total_gross_pnl": round(total_gross_pnl, 2),
            "total_friction_paid": round(total_friction, 2),
            "total_trades_count": total_trades,
            "overall_win_rate_pct": overall_win_rate,
            "overall_profit_factor": overall_pf,
            "expectancy_per_trade_dlr": overall_expectancy,
            "bootstrap_aggregate_pnl_95_ci": pnl_ci,
            "bootstrap_expectancy_95_ci": exp_ci,
            "concentration_diagnostics": {
                "best_aggregate_symbol": best_agg_sym,
                "top_3_symbols_share_pct": top3_sym_pct,
                "top_3_trades_share_pct": top3_trades_pct,
                "top_10_trades_share_pct": top10_trades_pct,
                "counterfactual_ex_best_trade_pnl": agg_ex_best_trade_pnl,
                "counterfactual_ex_top3_trades_pnl": agg_ex_top3_trades_pnl,
                "counterfactual_ex_best_symbol_pnl": agg_ex_best_sym_pnl,
            },
            "cost_stress_summary": {
                "profitable_months_1_0x": profitable_1_0x,
                "profitable_months_1_5x": profitable_1_5x,
                "profitable_months_2_0x": profitable_2_0x,
                "profitable_months_3_0x": profitable_3_0x,
                "aggregate_breakeven_cost_mult": agg_breakeven_mult,
            },
            "formal_verdicts": {
                "broader_validation_verdict": val_verdict,
                "concentration_verdict": conc_verdict,
                "engine_status": "ENGINE_V2_MORE_HISTORY_REQUIRED" if val_verdict == "BROADER_VALIDATION_MIXED" else ("ENGINE_V2_FORWARD_TEST_CANDIDATE" if val_verdict == "BROADER_VALIDATION_POSITIVE" else "ENGINE_V2_REDESIGN_REQUIRED"),
                "forward_paper_trading_gate": "MORE_REAL_HISTORICAL_VALIDATION" if val_verdict != "BROADER_VALIDATION_POSITIVE" or conc_verdict == "CONCENTRATION_STRUCTURAL" else "FORWARD_PAPER_TRADING_READY",
                "real_money_authorized": "REAL_MONEY_NOT_AUTHORIZED",
            },
        }
