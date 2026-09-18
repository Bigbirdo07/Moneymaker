"""
Real-Market Engine V3 Replay Runner for Phase 11B.
Executes two-stage ranking, selective entry gating (max 1 trade/day, edge >= 25 bps),
volatility-adjusted allocation, and tightened exit risk controls on real historical market data.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass
from src.data.real_data_firewall import RealDataFirewall
from src.features.real_market_feature_store_v3 import RealMarketFeatureStoreV3
from src.models.real_market_ranking_forecaster_v3 import RealMarketRankingForecasterV3, MultiHorizonPredictionV3
from src.signals.real_market_entry_model_v3 import RealMarketEntryModelV3, EntryDecisionV3
from src.signals.real_market_exit_model_v3 import RealMarketExitModelV3, ExitDecisionV3
from src.execution.real_market_allocator_v3 import RealMarketAllocatorV3, AllocationResultV3

logger = get_logger("replay.real_engine_v3_runner")


@dataclass
class RealTradeV3Record:
    """Immutable trade execution record under Engine V3 rules."""
    trade_id: str
    symbol: str
    session_date: str
    entry_timestamp: str
    exit_timestamp: str
    entry_price: float
    exit_price: float
    shares: int
    gross_pnl: float
    net_pnl: float
    return_pct: float
    total_friction: float
    bars_held: int
    target_horizon_min: int
    entry_reason: str
    exit_reason: str
    evidence_class: str = EvidenceClass.SIMULATED_EXECUTION_ON_REAL_MARKET_DATA.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RealEngineV3Runner:
    """
    Simulates autonomous execution of Engine V3 on real historical market data.
    """

    def __init__(
        self,
        forecaster: RealMarketRankingForecasterV3,
        entry_model: RealMarketEntryModelV3,
        exit_model: RealMarketExitModelV3,
        allocator: RealMarketAllocatorV3,
        feature_store: RealMarketFeatureStoreV3,
        starting_capital: float = 1000.0,
        symbols: Optional[List[str]] = None,
        base_spread_bps: float = 3.0,
        base_slippage_bps: float = 1.5,
        per_share_commission: float = 0.0005,
    ) -> None:
        self.forecaster = forecaster
        self.entry_model = entry_model
        self.exit_model = exit_model
        self.allocator = allocator
        self.feature_store = feature_store
        self.starting_capital = starting_capital
        self.symbols = symbols or []
        self.base_spread_bps = base_spread_bps
        self.base_slippage_bps = base_slippage_bps
        self.per_share_commission = per_share_commission

    def run_replay(
        self,
        features_df: pd.DataFrame,
        start_date: str,
        end_date: str,
        cost_multiplier: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Executes autonomous simulation of Engine V3 on cross-sectional feature matrix.
        """
        sub_df = features_df[(features_df["date_str"] >= start_date) & (features_df["date_str"] <= end_date)]
        if sub_df.empty:
            return {"status": "EMPTY", "trades": [], "decisions": [], "ending_capital": self.starting_capital, "net_pnl": 0.0}

        sub_df = sub_df.sort_values(["date_str", "time_str"]).reset_index(drop=True)

        current_capital = self.starting_capital
        available_cash = current_capital
        active_position: Optional[Dict[str, Any]] = None
        executed_trades: List[RealTradeV3Record] = []
        all_decisions: List[Dict[str, Any]] = []

        last_exit_bars_ago: Dict[str, int] = {}
        daily_trade_counts: Dict[str, int] = {}
        trade_counter = 0

        # Group by timestamp_et for synchronous contemporaneous ranking
        grouped = sub_df.groupby("timestamp_et", sort=False)

        for ts, frame in grouped:
            date_str = str(frame["date_str"].iloc[0])
            time_str = str(frame["time_str"].iloc[0])

            # Increment cooldown counters
            for sym in list(last_exit_bars_ago.keys()):
                last_exit_bars_ago[sym] += 1

            # 1. Manage Active Position Exits First
            if active_position is not None:
                pos_sym = active_position["symbol"]
                sym_row = frame[frame["symbol"] == pos_sym]
                if not sym_row.empty:
                    curr_price = float(sym_row["close_price"].iloc[0])
                    active_position["bars_held"] += 1
                    active_position["peak_price"] = max(active_position["peak_price"], curr_price)

                    # Get updated prediction for signal decay check
                    pos_pred = self.forecaster.predict_batch(sym_row)
                    edge_now = pos_pred[0].best_expected_net_edge_bps if pos_pred else 0.0

                    exit_dec = self.exit_model.evaluate_exit(
                        entry_price=active_position["entry_price"],
                        current_price=curr_price,
                        peak_price=active_position["peak_price"],
                        bars_held=active_position["bars_held"],
                        predicted_edge_bps=edge_now,
                        time_str=time_str,
                    )

                    if exit_dec.should_exit or time_str >= "15:45:00":
                        reason = exit_dec.exit_reason if exit_dec.should_exit else "EOD_FORCE_CLOSE"
                        # Calculate fill price with friction
                        half_spread_bps = (self.base_spread_bps * cost_multiplier)
                        half_slip_bps = (self.base_slippage_bps * cost_multiplier)
                        friction_rate = (half_spread_bps + half_slip_bps) / 10000.0

                        exit_fill_price = curr_price * (1.0 - friction_rate)
                        exit_comm = active_position["shares"] * self.per_share_commission * cost_multiplier

                        gross_pnl = (curr_price - active_position["entry_price"]) * active_position["shares"]
                        entry_friction = active_position["entry_friction"]
                        exit_friction = (curr_price * friction_rate * active_position["shares"]) + exit_comm
                        total_friction = entry_friction + exit_friction
                        net_pnl = gross_pnl - total_friction
                        ret_pct = (net_pnl / (active_position["entry_price"] * active_position["shares"])) * 100.0

                        trade_counter += 1
                        rec = RealTradeV3Record(
                            trade_id=f"REAL_V3_TR_{trade_counter:04d}",
                            symbol=pos_sym,
                            session_date=active_position["session_date"],
                            entry_timestamp=active_position["entry_timestamp"],
                            exit_timestamp=ts,
                            entry_price=active_position["entry_price"],
                            exit_price=curr_price,
                            shares=active_position["shares"],
                            gross_pnl=round(gross_pnl, 4),
                            net_pnl=round(net_pnl, 4),
                            return_pct=round(ret_pct, 4),
                            total_friction=round(total_friction, 4),
                            bars_held=active_position["bars_held"],
                            target_horizon_min=active_position["target_horizon_min"],
                            entry_reason=active_position["entry_reason"],
                            exit_reason=reason,
                        )
                        executed_trades.append(rec)

                        available_cash += (active_position["shares"] * curr_price) + net_pnl
                        current_capital += net_pnl
                        last_exit_bars_ago[pos_sym] = 0
                        active_position = None

            # 2. Evaluate Candidate Entries if No Active Position
            if active_position is None and time_str <= "14:30:00":
                # Batch prediction across all symbols present at timestamp T
                preds = self.forecaster.predict_batch(frame)
                current_daily_trades = daily_trade_counts.get(date_str, 0)

                entry_decisions = self.entry_model.evaluate_candidates(
                    predictions=preds,
                    current_daily_trades=current_daily_trades,
                    last_exit_bars_ago=last_exit_bars_ago,
                    has_active_position=False,
                )

                for ed in entry_decisions:
                    all_decisions.append(ed.to_dict())
                    if ed.action == "ENTER_LONG":
                        cand_row = frame[frame["symbol"] == ed.symbol].iloc[0]
                        cand_price = float(cand_row["close_price"])
                        cand_vol = float(cand_row.get("atr_14_bps", 20.0))

                        alloc = self.allocator.compute_allocation(
                            symbol=ed.symbol,
                            price=cand_price,
                            available_cash=available_cash,
                            total_equity=current_capital,
                            realized_vol_bps=cand_vol,
                            current_active_positions=0,
                        )

                        if alloc.allocation_status == "AUTHORIZED" and alloc.target_shares > 0:
                            half_spread_bps = (self.base_spread_bps * cost_multiplier)
                            half_slip_bps = (self.base_slippage_bps * cost_multiplier)
                            friction_rate = (half_spread_bps + half_slip_bps) / 10000.0
                            entry_fill_price = cand_price * (1.0 + friction_rate)
                            entry_comm = alloc.target_shares * self.per_share_commission * cost_multiplier
                            entry_fric_dollars = (cand_price * friction_rate * alloc.target_shares) + entry_comm

                            available_cash -= (alloc.target_shares * cand_price)

                            active_position = {
                                "symbol": ed.symbol,
                                "session_date": date_str,
                                "entry_timestamp": ts,
                                "entry_price": cand_price,
                                "shares": alloc.target_shares,
                                "peak_price": cand_price,
                                "bars_held": 0,
                                "target_horizon_min": ed.target_horizon_min,
                                "entry_reason": ed.decision_reason,
                                "entry_friction": entry_fric_dollars,
                            }
                            daily_trade_counts[date_str] = current_daily_trades + 1
                            break

        total_net_pnl = sum(t.net_pnl for t in executed_trades)
        total_gross_pnl = sum(t.gross_pnl for t in executed_trades)
        total_friction_paid = sum(t.total_friction for t in executed_trades)

        return {
            "status": "COMPLETED",
            "trades": executed_trades,
            "decisions": all_decisions,
            "starting_capital": self.starting_capital,
            "ending_capital": round(current_capital, 2),
            "net_pnl": round(total_net_pnl, 2),
            "gross_pnl": round(total_gross_pnl, 2),
            "total_friction": round(total_friction_paid, 2),
            "total_trades": len(executed_trades),
        }
