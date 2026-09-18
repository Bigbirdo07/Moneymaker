"""
Autonomous Trading Session Controller.
Orchestrates the complete institutional intraday lifecycle from premarket scanning
to minute-by-minute position monitoring, opportunity re-ranking, risk governance,
and end-of-day oracle reconciliation.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass, OrderSide, PortfolioState, Position
from src.data.calendar import ET_TZ, UTC_TZ, TradingCalendar, REGULAR_OPEN, REGULAR_CLOSE
from src.data.historical_market_data import HistoricalMarketDataManager
from src.evaluation.hindsight_oracle import HindsightOracle, OracleTradeBenchmark, ProfitCaptureReport
from src.execution.capital_allocator import AutonomousCapitalAllocator, PortfolioAllocationPlan
from src.execution.replay_execution_simulator import ReplayExecutionSimulator, ReplaySimulatedFill
from src.models.multi_horizon_forecaster import MultiHorizonForecaster
from src.ranking.opportunity_ranker import OpportunityRanker
from src.replay.market_replay_engine import HistoricalMarketReplayEngine
from src.signals.entry_model import EntryDecision, EntryDecisionModel
from src.signals.exit_model import ExitDecision, ExitDecisionModel
from src.signals.premarket_scanner import PremarketCandidate, PremarketOpportunityScanner

logger = get_logger("replay.session_controller")


@dataclass
class ReplayTradeRecord:
    """Complete round-trip trade record from autonomous session replay."""
    trade_id: str
    symbol: str
    session_date: str
    entry_timestamp: str
    exit_timestamp: str
    entry_price: float
    exit_price: float
    shares: int | float
    gross_pnl: float
    net_pnl: float
    return_pct: float
    spread_cost: float
    slippage_cost: float
    commission_cost: float
    total_friction: float
    bars_held: int
    entry_reason: str
    exit_reason_category: str
    entry_quality: str  # GOOD_ENTRY, EARLY_ENTRY, LATE_ENTRY, FALSE_POSITIVE, HIGH_COST_ENTRY, LOW_EDGE_ENTRY
    exit_quality: str   # GOOD_EXIT, EARLY_EXIT, LATE_EXIT, LOSS_AVOIDANCE, STOP_OUT, SESSION_CLOSE, SIGNAL_DECAY, BETTER_OPPORTUNITY
    mfe_bps: float
    mae_bps: float
    profit_capture_ratio: float
    evidence_class: str = EvidenceClass.HISTORICAL_REPLAY.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DailySessionReport:
    """Comprehensive daily performance and telemetry report for an autonomous session."""
    session_date: str
    starting_capital: float
    ending_capital: float
    gross_return_pct: float
    net_return_pct: float
    net_pnl_dollars: float
    total_friction_dollars: float
    total_trades_count: int
    winning_trades_count: int
    win_rate_pct: float
    average_winner_dollars: float
    average_loser_dollars: float
    profit_factor: float
    max_intraday_drawdown_pct: float
    cash_utilization_pct: float
    premarket_candidates_count: int
    decisions_logged_count: int
    avg_profit_capture_ratio: float
    entry_quality_breakdown: Dict[str, int]
    exit_quality_breakdown: Dict[str, int]
    trades: List[ReplayTradeRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_date": self.session_date,
            "starting_capital": self.starting_capital,
            "ending_capital": self.ending_capital,
            "gross_return_pct": self.gross_return_pct,
            "net_return_pct": self.net_return_pct,
            "net_pnl_dollars": self.net_pnl_dollars,
            "total_friction_dollars": self.total_friction_dollars,
            "total_trades_count": self.total_trades_count,
            "winning_trades_count": self.winning_trades_count,
            "win_rate_pct": self.win_rate_pct,
            "average_winner_dollars": self.average_winner_dollars,
            "average_loser_dollars": self.average_loser_dollars,
            "profit_factor": self.profit_factor,
            "max_intraday_drawdown_pct": self.max_intraday_drawdown_pct,
            "cash_utilization_pct": self.cash_utilization_pct,
            "premarket_candidates_count": self.premarket_candidates_count,
            "decisions_logged_count": self.decisions_logged_count,
            "avg_profit_capture_ratio": self.avg_profit_capture_ratio,
            "entry_quality_breakdown": self.entry_quality_breakdown,
            "exit_quality_breakdown": self.exit_quality_breakdown,
            "trades": [t.to_dict() for t in self.trades],
        }


class AutonomousTradingSessionController:
    """
    Autonomous Trading Session Controller managing the daily lifecycle for a $1,000 portfolio.
    """

    def __init__(
        self,
        replay_engine: HistoricalMarketReplayEngine,
        initial_capital: float = 1000.0,
        rerank_interval_minutes: int = 5,
    ) -> None:
        self.replay_engine = replay_engine
        self.initial_capital = initial_capital
        self.rerank_interval_minutes = rerank_interval_minutes

        self.premarket_scanner = PremarketOpportunityScanner()
        self.forecaster = MultiHorizonForecaster()
        self.opportunity_ranker = OpportunityRanker()
        self.entry_model = EntryDecisionModel()
        self.exit_model = ExitDecisionModel()
        self.capital_allocator = AutonomousCapitalAllocator()
        self.execution_simulator = ReplayExecutionSimulator()
        self.hindsight_oracle = HindsightOracle()

        # Decision dataset accumulators
        self.entry_dataset_records: List[Dict[str, Any]] = []
        self.exit_dataset_records: List[Dict[str, Any]] = []

    def run_session(
        self,
        session_date: date | str,
        universe_symbols: List[str],
    ) -> DailySessionReport:
        """
        Executes a full 08:30–16:00 ET historical replay session across target universe.
        """
        if isinstance(session_date, str):
            session_date = datetime.strptime(session_date, "%Y-%m-%d").date()

        sess_date_str = str(session_date)
        logger.info(f"Starting autonomous replay session for {sess_date_str} across {len(universe_symbols)} symbols...")

        # Initialize portfolio state ($1,000 USD initial capital)
        portfolio = PortfolioState(
            timestamp=datetime.combine(session_date, time(8, 30), tzinfo=ET_TZ).astimezone(UTC_TZ),
            cash=self.initial_capital,
            buying_power=self.initial_capital,
            positions={},
            portfolio_value=self.initial_capital,
            initial_capital=self.initial_capital,
        )

        completed_trades: List[ReplayTradeRecord] = []
        active_entry_fills: Dict[str, ReplaySimulatedFill] = {}
        high_water_marks: Dict[str, float] = {}
        low_water_marks: Dict[str, float] = {}
        pending_orders: List[Dict[str, Any]] = []  # Executed on next bar
        pm_candidates: List[PremarketCandidate] = []
        trade_counter = 0

        # Quality metrics breakdown
        entry_quality_counts = {k: 0 for k in ["GOOD_ENTRY", "EARLY_ENTRY", "LATE_ENTRY", "FALSE_POSITIVE", "HIGH_COST_ENTRY", "LOW_EDGE_ENTRY"]}
        exit_quality_counts = {k: 0 for k in ["GOOD_EXIT", "EARLY_EXIT", "LATE_EXIT", "LOSS_AVOIDANCE", "STOP_OUT", "SESSION_CLOSE", "SIGNAL_DECAY", "BETTER_OPPORTUNITY"]}

        # Minute-by-minute simulation loop
        for clock_utc, clock_et in self.replay_engine.iterate_session_minutes(session_date, include_premarket=True):
            time_et = clock_et.time()
            mins_to_close = TradingCalendar.get_minutes_to_close(clock_et)

            # 1. Execute Pending Next-Bar Orders
            if pending_orders:
                orders_to_execute = list(pending_orders)
                pending_orders.clear()
                for order in orders_to_execute:
                    sym = order["symbol"]
                    side = order["side"]
                    shares = order["shares"]
                    order_id = order["order_id"]
                    dec_ts = order["decision_timestamp"]

                    curr_bar = self.replay_engine.get_current_bar(sym)
                    if curr_bar is not None:
                        bar_dict = curr_bar.to_dict()
                        fill = self.execution_simulator.simulate_fill(
                            order_id=order_id,
                            symbol=sym,
                            side=side,
                            shares=shares,
                            decision_timestamp=dec_ts,
                            execution_bar=bar_dict,
                        )

                        if side == "BUY":
                            total_cost = (shares * fill.fill_price) + fill.commission_fee
                            if total_cost <= portfolio.cash + 0.01:
                                portfolio.cash -= total_cost
                                portfolio.total_fees += fill.commission_fee
                                portfolio.total_slippage += fill.slippage_cost

                                pos = Position(
                                    symbol=sym,
                                    shares=shares,
                                    avg_entry_price=fill.fill_price,
                                    current_price=fill.reference_price,
                                    entry_timestamp=clock_utc,
                                    bars_held=0,
                                )
                                portfolio.positions[sym] = pos
                                active_entry_fills[sym] = fill
                                high_water_marks[sym] = fill.fill_price
                                low_water_marks[sym] = fill.fill_price

                        elif side == "SELL" and sym in portfolio.positions:
                            pos = portfolio.positions[sym]
                            gross_proceeds = shares * fill.fill_price
                            net_proceeds = gross_proceeds - fill.commission_fee

                            portfolio.cash += net_proceeds
                            portfolio.total_fees += fill.commission_fee
                            portfolio.total_slippage += fill.slippage_cost

                            # Record completed trade
                            trade_counter += 1
                            entry_fill = active_entry_fills.get(sym)
                            entry_cost_basis = pos.shares * pos.avg_entry_price
                            gross_pnl = (pos.shares * fill.reference_price) - (pos.shares * (entry_fill.reference_price if entry_fill else pos.avg_entry_price))
                            total_fric = fill.total_friction + (entry_fill.total_friction if entry_fill else 0.0)
                            net_pnl = net_proceeds - entry_cost_basis

                            ret_pct = net_pnl / entry_cost_basis if entry_cost_basis > 0 else 0.0
                            mfe_bps = ((high_water_marks.get(sym, pos.avg_entry_price) - pos.avg_entry_price) / pos.avg_entry_price) * 10000.0
                            mae_bps = ((low_water_marks.get(sym, pos.avg_entry_price) - pos.avg_entry_price) / pos.avg_entry_price) * 10000.0

                            # Determine entry quality category
                            if ret_pct > 0.005:
                                entry_cat = "GOOD_ENTRY"
                            elif mfe_bps > 20.0 and ret_pct <= 0:
                                entry_cat = "LATE_ENTRY"
                            elif ret_pct < -0.010:
                                entry_cat = "FALSE_POSITIVE"
                            else:
                                entry_cat = "LOW_EDGE_ENTRY"
                            entry_quality_counts[entry_cat] += 1

                            # Determine exit quality category
                            exit_reason_cat = order.get("exit_reason_category", "SESSION_CLOSE")
                            if ret_pct > 0.010:
                                exit_cat = "GOOD_EXIT"
                            elif exit_reason_cat == "STOP_LOSS":
                                exit_cat = "STOP_OUT"
                            elif exit_reason_cat == "SESSION_CLOSE":
                                exit_cat = "SESSION_CLOSE"
                            elif exit_reason_cat == "SIGNAL_DECAY":
                                exit_cat = "SIGNAL_DECAY"
                            elif exit_reason_cat == "BETTER_OPPORTUNITY":
                                exit_cat = "BETTER_OPPORTUNITY"
                            elif ret_pct < 0 and mfe_bps > 30.0:
                                exit_cat = "LATE_EXIT"
                            else:
                                exit_cat = "EARLY_EXIT"
                            exit_quality_counts[exit_cat] += 1

                            # Profit capture via Hindsight Oracle
                            sym_session_bars = self.replay_engine.get_visible_bars(sym, lookback_bars=450)
                            oracle_bench = self.hindsight_oracle.compute_session_oracle_bounds(sym, sym_session_bars)
                            pc_report = self.hindsight_oracle.evaluate_profit_capture(
                                symbol=sym,
                                realized_entry_price=pos.avg_entry_price,
                                realized_exit_price=fill.fill_price,
                                realized_net_pnl=net_pnl,
                                oracle_benchmark=oracle_bench,
                            )

                            completed_trades.append(ReplayTradeRecord(
                                trade_id=f"TR_{sess_date_str}_{trade_counter:04d}",
                                symbol=sym,
                                session_date=sess_date_str,
                                entry_timestamp=str(pos.entry_timestamp),
                                exit_timestamp=str(clock_utc),
                                entry_price=pos.avg_entry_price,
                                exit_price=fill.fill_price,
                                shares=pos.shares,
                                gross_pnl=round(gross_pnl, 4),
                                net_pnl=round(net_pnl, 4),
                                return_pct=round(ret_pct, 6),
                                spread_cost=round(fill.spread_cost + (entry_fill.spread_cost if entry_fill else 0), 4),
                                slippage_cost=round(fill.slippage_cost + (entry_fill.slippage_cost if entry_fill else 0), 4),
                                commission_cost=round(fill.commission_fee + (entry_fill.commission_fee if entry_fill else 0), 4),
                                total_friction=round(total_fric, 4),
                                bars_held=pos.bars_held,
                                entry_reason=order.get("entry_reason", "POSITIVE_NET_EDGE"),
                                exit_reason_category=exit_reason_cat,
                                entry_quality=entry_cat,
                                exit_quality=exit_cat,
                                mfe_bps=round(mfe_bps, 2),
                                mae_bps=round(mae_bps, 2),
                                profit_capture_ratio=pc_report.profit_capture_ratio,
                            ))

                            del portfolio.positions[sym]
                            if sym in active_entry_fills:
                                del active_entry_fills[sym]
                            if sym in high_water_marks:
                                del high_water_marks[sym]
                            if sym in low_water_marks:
                                del low_water_marks[sym]

            # 2. Mark-to-market positions
            for sym, pos in list(portfolio.positions.items()):
                curr_bar = self.replay_engine.get_current_bar(sym)
                if curr_bar is not None:
                    cp = float(curr_bar["close"])
                    pos.update_price(cp)
                    pos.bars_held += 1
                    high_water_marks[sym] = max(high_water_marks.get(sym, cp), cp)
                    low_water_marks[sym] = min(low_water_marks.get(sym, cp), cp)

            portfolio.timestamp = clock_utc
            portfolio.update_metrics()

            # 3. Schedule Phase Actions
            # Phase A: 08:30–09:15 Premarket Scan
            if time(8, 30) <= time_et <= time(9, 15):
                if time_et == time(9, 15):
                    pm_candidates = self.premarket_scanner.scan_universe(self.replay_engine, universe_symbols)
                    self.replay_engine.record_decision_event(
                        symbol="UNIVERSE",
                        event_type="PREMARKET_SCAN",
                        decision_action=f"IDENTIFIED_{len(pm_candidates)}_CANDIDATES",
                        decision_rationale=f"Premarket scan completed with {len(pm_candidates)} eligible opportunities.",
                        features_snapshot={"candidate_symbols": [c.symbol for c in pm_candidates]},
                    )

            # Phase B: 09:30–15:50 Regular Session Intraday Trading
            elif time(9, 30) <= time_et <= time(15, 50):
                # A. Evaluate Exits for all active positions
                best_competing_edge = 0.0
                for sym, pos in list(portfolio.positions.items()):
                    vis_df = self.replay_engine.get_visible_bars(sym, lookback_bars=60)
                    pred = self.forecaster.predict(sym, clock_utc, vis_df)

                    exit_dec = self.exit_model.evaluate_exit(
                        position=pos,
                        current_price=pos.current_price,
                        prediction=pred,
                        minutes_to_close=mins_to_close,
                        best_competing_edge_bps=best_competing_edge,
                        high_water_mark=high_water_marks.get(sym),
                        low_water_mark=low_water_marks.get(sym),
                    )

                    # Record in DS_EXIT_DECISION_V1 dataset
                    self.exit_dataset_records.append({
                        "timestamp": str(clock_utc),
                        "symbol": sym,
                        "entry_price": pos.avg_entry_price,
                        "current_price": pos.current_price,
                        "bars_held": pos.bars_held,
                        "unrealized_pnl_bps": exit_dec.unrealized_pnl_bps,
                        "current_edge_bps": exit_dec.current_edge_bps,
                        "mfe_bps": exit_dec.mfe_bps,
                        "mae_bps": exit_dec.mae_bps,
                        "action_taken": exit_dec.action,
                        "reason_category": exit_dec.reason_category,
                    })

                    if exit_dec.is_exit_triggered:
                        pending_orders.append({
                            "order_id": f"ORD_OUT_{len(completed_trades)+len(pending_orders)+1}",
                            "symbol": sym,
                            "side": "SELL",
                            "shares": pos.shares,
                            "decision_timestamp": str(clock_utc),
                            "exit_reason_category": exit_dec.reason_category,
                        })
                        self.replay_engine.record_decision_event(
                            symbol=sym,
                            event_type="EXIT_DECISION",
                            decision_action=exit_dec.action,
                            decision_rationale=exit_dec.reason_category,
                            features_snapshot={"pnl_bps": exit_dec.unrealized_pnl_bps, "bars_held": exit_dec.bars_held},
                        )

                # B. Periodic Re-Ranking & Entry Evaluation (Every rerank_interval_minutes, e.g. 5m)
                if (clock_et.minute % self.rerank_interval_minutes == 0) and (mins_to_close > 25.0) and len(portfolio.positions) < 4:
                    candidate_decisions: List[Tuple[EntryDecision, float]] = []

                    for sym in universe_symbols:
                        if sym in portfolio.positions:
                            continue
                        vis_df = self.replay_engine.get_visible_bars(sym, lookback_bars=60)
                        if vis_df.empty:
                            continue
                        pred = self.forecaster.predict(sym, clock_utc, vis_df)
                        curr_p = float(vis_df["close"].iloc[-1])
                        sp_bps = (float(vis_df["spread"].iloc[-1]) / curr_p * 10000.0) if "spread" in vis_df else 2.5

                        entry_dec = self.entry_model.evaluate_entry(
                            prediction=pred,
                            current_spread_bps=sp_bps,
                            portfolio=portfolio,
                            minutes_to_close=mins_to_close,
                        )

                        # Record in DS_ENTRY_DECISION_V1 dataset
                        self.entry_dataset_records.append({
                            "timestamp": str(clock_utc),
                            "symbol": sym,
                            "current_price": curr_p,
                            "expected_gross_bps": entry_dec.expected_gross_return_bps,
                            "estimated_friction_bps": entry_dec.estimated_friction_bps,
                            "expected_net_edge_bps": entry_dec.expected_net_edge_bps,
                            "probability_positive": entry_dec.probability_positive,
                            "decision_action": entry_dec.action,
                            "decision_reason": entry_dec.reason,
                        })

                        if entry_dec.action == "BUY" and entry_dec.is_authorized:
                            candidate_decisions.append((entry_dec, curr_p))

                    if candidate_decisions:
                        # Allocate capital
                        alloc_plan = self.capital_allocator.allocate(
                            timestamp=str(clock_utc),
                            portfolio=portfolio,
                            candidate_entries=candidate_decisions,
                        )

                        for target in alloc_plan.targets:
                            if target.target_shares > 0:
                                pending_orders.append({
                                    "order_id": f"ORD_IN_{len(completed_trades)+len(pending_orders)+1}",
                                    "symbol": target.symbol,
                                    "side": "BUY",
                                    "shares": target.target_shares,
                                    "decision_timestamp": str(clock_utc),
                                    "entry_reason": "POSITIVE_NET_EDGE_ALLOCATED",
                                })
                                self.replay_engine.record_decision_event(
                                    symbol=target.symbol,
                                    event_type="ENTRY_DECISION",
                                    decision_action="BUY",
                                    decision_rationale=f"Allocated {target.target_shares} shares (${target.target_dollars:.2f})",
                                    features_snapshot={"edge_bps": target.expected_edge_bps, "target_dollars": target.target_dollars},
                                )

            # Phase C: 15:50–16:00 Session End Closeout (Liquidate all remaining active positions)
            elif time_et > time(15, 50):
                for sym, pos in list(portfolio.positions.items()):
                    if not any(o["symbol"] == sym and o["side"] == "SELL" for o in pending_orders):
                        pending_orders.append({
                            "order_id": f"ORD_FORCE_OUT_{len(completed_trades)+len(pending_orders)+1}",
                            "symbol": sym,
                            "side": "SELL",
                            "shares": pos.shares,
                            "decision_timestamp": str(clock_utc),
                            "exit_reason_category": "SESSION_CLOSE",
                        })

        # Calculate session summary performance
        final_equity = portfolio.portfolio_value
        net_pnl = final_equity - self.initial_capital
        gross_pnl = net_pnl + portfolio.total_fees + portfolio.total_slippage
        gross_ret = gross_pnl / self.initial_capital
        net_ret = net_pnl / self.initial_capital

        winning_trades = [t for t in completed_trades if t.net_pnl > 0]
        losing_trades = [t for t in completed_trades if t.net_pnl < 0]

        win_rate = (len(winning_trades) / len(completed_trades) * 100.0) if completed_trades else 0.0
        avg_win = float(np.mean([t.net_pnl for t in winning_trades])) if winning_trades else 0.0
        avg_loss = float(np.mean([t.net_pnl for t in losing_trades])) if losing_trades else 0.0
        gross_wins = sum([t.net_pnl for t in winning_trades])
        gross_losses = abs(sum([t.net_pnl for t in losing_trades]))
        profit_factor = (gross_wins / gross_losses) if gross_losses > 0 else (99.0 if gross_wins > 0 else 1.0)

        avg_capture = float(np.mean([t.profit_capture_ratio for t in completed_trades])) if completed_trades else 0.0

        return DailySessionReport(
            session_date=sess_date_str,
            starting_capital=self.initial_capital,
            ending_capital=round(final_equity, 2),
            gross_return_pct=round(gross_ret * 100.0, 4),
            net_return_pct=round(net_ret * 100.0, 4),
            net_pnl_dollars=round(net_pnl, 4),
            total_friction_dollars=round(portfolio.total_fees + portfolio.total_slippage, 4),
            total_trades_count=len(completed_trades),
            winning_trades_count=len(winning_trades),
            win_rate_pct=round(win_rate, 2),
            average_winner_dollars=round(avg_win, 4),
            average_loser_dollars=round(avg_loss, 4),
            profit_factor=round(profit_factor, 2),
            max_intraday_drawdown_pct=round(portfolio.max_drawdown_pct * 100.0, 2),
            cash_utilization_pct=round((1.0 - (portfolio.cash / final_equity)) * 100.0 if final_equity > 0 else 0, 2),
            premarket_candidates_count=len(pm_candidates),
            decisions_logged_count=len(self.replay_engine._event_logs),
            avg_profit_capture_ratio=round(avg_capture, 4),
            entry_quality_breakdown=entry_quality_counts,
            exit_quality_breakdown=exit_quality_counts,
            trades=completed_trades,
        )
