"""Regime-conditional breakdown analytics for models and strategies."""

from __future__ import annotations

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, brier_score_loss

from src.backtest.engine import CompletedTrade


class RegimeAnalyzer:
    """Analyzes model predictions, calibration, and trade outcomes conditional on market regimes."""

    @staticmethod
    def analyze_predictions_by_regime(prediction_df: pd.DataFrame) -> pd.DataFrame:
        """Computes sample counts, accuracy, and Brier score across regimes."""
        if prediction_df.empty or "regime" not in prediction_df.columns:
            return pd.DataFrame()

        rows = []
        for regime_name, group in prediction_df.groupby("regime"):
            n_samples = len(group)
            if n_samples < 5 or "actual_label" not in group or group["actual_label"].isna().any():
                continue
            
            y_true = group["actual_label"].values
            y_pred = group["predicted_label"].values
            y_prob = group["p_up"].values

            acc = float(accuracy_score(y_true, y_pred))
            brier = float(brier_score_loss(y_true, y_prob))
            pos_rate = float(np.mean(y_true))
            pred_pos_rate = float(np.mean(y_pred))

            rows.append({
                "regime": regime_name,
                "sample_count": n_samples,
                "accuracy": round(acc, 4),
                "brier_score": round(brier, 4),
                "actual_up_rate": round(pos_rate, 4),
                "predicted_up_rate": round(pred_pos_rate, 4),
            })
        return pd.DataFrame(rows)

    @staticmethod
    def analyze_trades_by_regime(trades: List[CompletedTrade], regime_map: Dict[pd.Timestamp, str]) -> pd.DataFrame:
        """Computes trade frequency, win rate, and net PnL broken down by market regime."""
        if not trades:
            return pd.DataFrame()

        records = []
        for t in trades:
            reg = regime_map.get(t.entry_timestamp, "UNKNOWN")
            records.append({
                "regime": reg,
                "net_pnl": t.net_pnl,
                "is_win": 1 if t.net_pnl > 0 else 0,
            })
        df = pd.DataFrame(records)
        
        rows = []
        for reg_name, group in df.groupby("regime"):
            n = len(group)
            win_r = float(group["is_win"].mean()) if n > 0 else 0.0
            tot_pnl = float(group["net_pnl"].sum())
            avg_pnl = float(group["net_pnl"].mean()) if n > 0 else 0.0

            rows.append({
                "regime": reg_name,
                "trade_count": n,
                "win_rate": round(win_r, 4),
                "total_net_pnl": round(tot_pnl, 4),
                "avg_trade_pnl": round(avg_pnl, 4),
            })
        return pd.DataFrame(rows)
