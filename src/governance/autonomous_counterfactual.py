"""
Four-Book Multi-Execution Tracking & Autonomous Counterfactual Engine for Phase 5B.
Maintains continuous parallel tracking of:
- Book A: Actual Live Governed Micro Fills (Real Money with Human Approval)
- Book B: Realistic Conservative Shadow Simulation (Bid/Ask Queue Placement)
- Book C: Broker Paper Trading Gateway
- Book D: Autonomous Counterfactual Strategy (Automatic Execution without Human Deliberation)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.broker.adapter import BrokerFill, BrokerOrder, OrderSide, OrderStatus, OrderType
from src.governance.human_approval import (
    ApprovalAction,
    ApprovalDisplayMode,
    HumanApprovalGate,
    HumanApprovalRecord,
    OperatorReasonCode,
    ProposedOrderCard,
)
from src.portfolio.shadow_portfolio import ExitReason, ShadowPaperPortfolio, ShadowPosition


@dataclass
class FourBookComparisonRecord:
    decision_id: str
    symbol: str
    decision_timestamp: pd.Timestamp
    decision_midprice: float
    
    # Book A: Live Governed Micro
    book_a_executed: bool
    book_a_fill_price: Optional[float]
    book_a_shortfall_bps: Optional[float]
    book_a_net_pnl_bps: Optional[float]
    
    # Book B: Realistic Conservative Shadow
    book_b_executed: bool
    book_b_fill_price: float
    book_b_shortfall_bps: float
    book_b_net_pnl_bps: float
    
    # Book C: Broker Paper
    book_c_executed: bool
    book_c_fill_price: float
    book_c_shortfall_bps: float
    book_c_net_pnl_bps: float
    
    # Book D: Autonomous Counterfactual (Zero Human Latency)
    book_d_executed: bool
    book_d_fill_price: float
    book_d_shortfall_bps: float
    book_d_net_pnl_bps: float


class FourBookExecutionLedger:
    """Manages parallel multi-book tracking and comparative statistics across Books A, B, C, D."""

    def __init__(self, initial_cash: float = 1000.0, base_friction_bps: float = 3.35):
        self.initial_cash = initial_cash
        self.base_friction_bps = base_friction_bps
        
        # Internal Book Ledgers
        self.book_a_portfolio = ShadowPaperPortfolio(initial_cash=initial_cash, transaction_cost_bps=base_friction_bps)
        self.book_b_portfolio = ShadowPaperPortfolio(initial_cash=initial_cash, transaction_cost_bps=3.50) # Conservative shadow
        self.book_c_portfolio = ShadowPaperPortfolio(initial_cash=initial_cash, transaction_cost_bps=3.10) # Paper
        self.book_d_portfolio = ShadowPaperPortfolio(initial_cash=initial_cash, transaction_cost_bps=base_friction_bps) # Autonomous counterfactual
        
        self.comparison_records: List[FourBookComparisonRecord] = []

    def record_decision_cycle(
        self,
        card: ProposedOrderCard,
        operator_record: Optional[HumanApprovalRecord],
        live_executed: bool,
        live_fill_price: Optional[float],
        future_gross_return_bps: float,
    ) -> FourBookComparisonRecord:
        """
        Record a single decision across all four books and update internal accounting.
        """
        mid = (card.current_bid + card.current_ask) / 2.0
        
        # Book A: Live Governed Micro
        shortfall_a = ((live_fill_price - mid) / mid * 10000.0) if (live_executed and live_fill_price) else None
        net_pnl_a = (future_gross_return_bps - self.base_friction_bps - (shortfall_a or 0.0)) if live_executed else None
        
        # Book B: Realistic Shadow (Simulated passive queue fill)
        fill_b = card.current_ask * 1.00005
        shortfall_b = ((fill_b - mid) / mid) * 10000.0
        net_pnl_b = future_gross_return_bps - 3.50
        
        # Book C: Broker Paper
        fill_c = card.current_ask
        shortfall_c = ((fill_c - mid) / mid) * 10000.0
        net_pnl_c = future_gross_return_bps - 3.10
        
        # Book D: Autonomous Counterfactual (Executed automatically at prompt decision price)
        fill_d = card.current_ask * 1.00002 # Immediate submission fill
        shortfall_d = ((fill_d - mid) / mid) * 10000.0
        net_pnl_d = future_gross_return_bps - self.base_friction_bps
        
        rec = FourBookComparisonRecord(
            decision_id=card.proposal_id,
            symbol=card.symbol,
            decision_timestamp=card.decision_timestamp,
            decision_midprice=mid,
            book_a_executed=live_executed,
            book_a_fill_price=live_fill_price,
            book_a_shortfall_bps=shortfall_a,
            book_a_net_pnl_bps=net_pnl_a,
            book_b_executed=True,
            book_b_fill_price=fill_b,
            book_b_shortfall_bps=shortfall_b,
            book_b_net_pnl_bps=net_pnl_b,
            book_c_executed=True,
            book_c_fill_price=fill_c,
            book_c_shortfall_bps=shortfall_c,
            book_c_net_pnl_bps=net_pnl_c,
            book_d_executed=True,
            book_d_fill_price=fill_d,
            book_d_shortfall_bps=shortfall_d,
            book_d_net_pnl_bps=net_pnl_d,
        )
        self.comparison_records.append(rec)
        return rec

    def compute_summary_matrix(self) -> Dict[str, Dict[str, float]]:
        """Generate complete comparative performance matrix for Books A, B, C, D."""
        if not self.comparison_records:
            return {}

        recs = self.comparison_records
        
        # Book A
        a_recs = [r for r in recs if r.book_a_executed and r.book_a_net_pnl_bps is not None]
        a_pnls = [r.book_a_net_pnl_bps for r in a_recs]
        a_shortfalls = [r.book_a_shortfall_bps for r in a_recs if r.book_a_shortfall_bps is not None]
        
        # Book B
        b_pnls = [r.book_b_net_pnl_bps for r in recs]
        b_shortfalls = [r.book_b_shortfall_bps for r in recs]
        
        # Book C
        c_pnls = [r.book_c_net_pnl_bps for r in recs]
        c_shortfalls = [r.book_c_shortfall_bps for r in recs]
        
        # Book D
        d_pnls = [r.book_d_net_pnl_bps for r in recs]
        d_shortfalls = [r.book_d_shortfall_bps for r in recs]

        def _calc_metrics(pnls: List[float], shortfalls: List[float], total_trades: int) -> Dict[str, float]:
            if not pnls:
                return {
                    "trade_count": 0,
                    "net_expectancy_bps": 0.0,
                    "win_rate_pct": 0.0,
                    "profit_factor": 0.0,
                    "mean_shortfall_bps": 0.0,
                    "max_drawdown_bps": 0.0,
                }
            wins = [p for p in pnls if p > 0]
            losses = [abs(p) for p in pnls if p < 0]
            pf = (sum(wins) / sum(losses)) if losses and sum(losses) > 0 else (10.0 if wins else 1.0)
            
            # Cumulative drawdown in bps
            cum = np.cumsum(pnls)
            peaks = np.maximum.accumulate(cum)
            dd = peaks - cum
            max_dd = float(np.max(dd)) if len(dd) > 0 else 0.0

            return {
                "trade_count": total_trades,
                "net_expectancy_bps": float(np.mean(pnls)),
                "win_rate_pct": float(len(wins) / len(pnls) * 100.0),
                "profit_factor": float(pf),
                "mean_shortfall_bps": float(np.mean(shortfalls)),
                "max_drawdown_bps": max_dd,
            }

        return {
            "Book_A_Live_Governed": _calc_metrics(a_pnls, a_shortfalls, len(a_recs)),
            "Book_B_Realistic_Shadow": _calc_metrics(b_pnls, b_shortfalls, len(recs)),
            "Book_C_Broker_Paper": _calc_metrics(c_pnls, c_shortfalls, len(recs)),
            "Book_D_Autonomous_Counterfactual": _calc_metrics(d_pnls, d_shortfalls, len(recs)),
        }
