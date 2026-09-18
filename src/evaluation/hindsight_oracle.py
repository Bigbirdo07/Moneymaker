"""
Hindsight Oracle & Profit Capture Ratio Evaluation Engine.
Strictly evaluation-only. Never feeds production or simulated trading decisions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass

logger = get_logger("evaluation.hindsight_oracle")


@dataclass
class OracleTradeBenchmark:
    """Theoretical optimal intraday trade bounds identified in post-hoc hindsight."""
    symbol: str
    session_date: str
    optimal_entry_time: str
    optimal_entry_price: float
    optimal_exit_time: str
    optimal_exit_price: float
    max_attainable_return_pct: float
    max_attainable_return_bps: float
    lowest_session_price: float
    highest_session_price: float
    oracle_tag: str = "HINDSIGHT_ONLY"
    tradable: bool = False
    evidence_class: str = EvidenceClass.HINDSIGHT_ORACLE.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProfitCaptureReport:
    """Comparison of realized model performance against theoretical oracle upper bounds."""
    session_date: str
    symbol: str
    realized_net_return_pct: float
    realized_net_pnl_dollars: float
    oracle_feasible_return_pct: float
    profit_capture_ratio: float
    entry_efficiency_pct: float
    exit_efficiency_pct: float
    missed_upside_bps: float
    evidence_class: str = EvidenceClass.HINDSIGHT_ORACLE.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HindsightOracle:
    """
    Computes theoretical optimal performance benchmarks using full session hindsight.
    STRICT NOTICE: All outputs are labeled HINDSIGHT_ONLY and are NOT TRADABLE.
    """

    def __init__(self, min_holding_bars: int = 5) -> None:
        self.min_holding_bars = min_holding_bars

    def compute_session_oracle_bounds(
        self,
        symbol: str,
        session_df: pd.DataFrame,
    ) -> OracleTradeBenchmark:
        """
        Calculates the maximum feasible long return within a single trading day session.
        """
        if len(session_df) < self.min_holding_bars:
            return OracleTradeBenchmark(
                symbol=symbol,
                session_date="N/A",
                optimal_entry_time="N/A",
                optimal_entry_price=0.0,
                optimal_exit_time="N/A",
                optimal_exit_price=0.0,
                max_attainable_return_pct=0.0,
                max_attainable_return_bps=0.0,
                lowest_session_price=0.0,
                highest_session_price=0.0,
            )

        df = session_df.sort_values("timestamp").reset_index(drop=True)
        session_date = str(df["timestamp"].dt.tz_convert("America/New_York").dt.date.iloc[0])

        lows = df["low"].values
        highs = df["high"].values
        timestamps = df["timestamp"].astype(str).values

        n = len(df)
        best_ret = -1.0
        best_entry_idx = 0
        best_exit_idx = 0

        # Find max(high[j] / low[i] - 1) for j >= i + min_holding_bars
        for i in range(n - self.min_holding_bars):
            entry_p = lows[i]
            if entry_p <= 0:
                continue
            future_highs = highs[i + self.min_holding_bars:]
            max_future_idx = np.argmax(future_highs) + i + self.min_holding_bars
            max_future_p = highs[max_future_idx]

            ret = (max_future_p - entry_p) / entry_p
            if ret > best_ret:
                best_ret = ret
                best_entry_idx = i
                best_exit_idx = max_future_idx

        opt_entry_p = float(lows[best_entry_idx])
        opt_exit_p = float(highs[best_exit_idx])

        return OracleTradeBenchmark(
            symbol=symbol,
            session_date=session_date,
            optimal_entry_time=timestamps[best_entry_idx],
            optimal_entry_price=round(opt_entry_p, 4),
            optimal_exit_time=timestamps[best_exit_idx],
            optimal_exit_price=round(opt_exit_p, 4),
            max_attainable_return_pct=round(best_ret, 6),
            max_attainable_return_bps=round(best_ret * 10000.0, 2),
            lowest_session_price=round(float(np.min(lows)), 4),
            highest_session_price=round(float(np.max(highs)), 4),
        )

    def evaluate_profit_capture(
        self,
        symbol: str,
        realized_entry_price: float,
        realized_exit_price: float,
        realized_net_pnl: float,
        oracle_benchmark: OracleTradeBenchmark,
    ) -> ProfitCaptureReport:
        """
        Evaluates what fraction of the theoretical feasible opportunity was captured by the strategy.
        """
        realized_ret = (realized_exit_price - realized_entry_price) / realized_entry_price if realized_entry_price > 0 else 0.0
        oracle_ret = oracle_benchmark.max_attainable_return_pct

        if oracle_ret > 0.0001:
            capture_ratio = max(-2.0, min(2.0, realized_ret / oracle_ret))
        else:
            capture_ratio = 1.0 if realized_ret >= 0 else 0.0

        # Entry efficiency: How close entry price was to optimal lowest entry
        entry_eff = (oracle_benchmark.highest_session_price - realized_entry_price) / (oracle_benchmark.highest_session_price - oracle_benchmark.lowest_session_price + 1e-6)
        entry_eff = float(np.clip(entry_eff, 0.0, 1.0))

        # Exit efficiency: How close exit price was to optimal highest exit
        exit_eff = (realized_exit_price - oracle_benchmark.lowest_session_price) / (oracle_benchmark.highest_session_price - oracle_benchmark.lowest_session_price + 1e-6)
        exit_eff = float(np.clip(exit_eff, 0.0, 1.0))

        missed_bps = max(0.0, (oracle_benchmark.optimal_exit_price - realized_exit_price) / realized_entry_price * 10000.0) if realized_entry_price > 0 else 0.0

        return ProfitCaptureReport(
            session_date=oracle_benchmark.session_date,
            symbol=symbol,
            realized_net_return_pct=round(realized_ret, 6),
            realized_net_pnl_dollars=round(realized_net_pnl, 4),
            oracle_feasible_return_pct=round(oracle_ret, 6),
            profit_capture_ratio=round(capture_ratio, 4),
            entry_efficiency_pct=round(entry_eff * 100.0, 2),
            exit_efficiency_pct=round(exit_eff * 100.0, 2),
            missed_upside_bps=round(missed_bps, 2),
        )
