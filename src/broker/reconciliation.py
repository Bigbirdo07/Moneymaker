"""
Broker Reconciliation & Dual Execution Tracking (Phase 3B, 5A, 6A, and Phase F).

Reconciles internal portfolio and position states against broker ground truth at
startup, intraday intervals, and post-market close.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd

from src.portfolio.position_lifecycle import ManagedPosition
from src.portfolio.strategy_capital_ledger import StrategyCapitalLedger

logger = logging.getLogger("src.broker.reconciliation")


class KillSwitchCommand(str, Enum):
    PAUSE_NEW_ORDERS = "PAUSE_NEW_ORDERS"
    RESUME_NEW_ORDERS = "RESUME_NEW_ORDERS"
    CANCEL_ALL_OPEN_ORDERS = "CANCEL_ALL_OPEN_ORDERS"
    CLOSE_ALL_POSITIONS = "CLOSE_ALL_POSITIONS"
    DISABLE_SYMBOL = "DISABLE_SYMBOL"
    ENABLE_SYMBOL = "ENABLE_SYMBOL"
    DISABLE_STRATEGY = "DISABLE_STRATEGY"
    FULL_SYSTEM_LOCKOUT = "FULL_SYSTEM_LOCKOUT"


@dataclass
class DualExecutionComparison:
    decision_id: str
    symbol: str
    side: str
    decision_midprice: float
    quote_bid: float
    quote_ask: float
    spread_bps: float

    # Broker Paper Execution
    broker_fill_price: float
    broker_fill_ts: pd.Timestamp
    broker_slippage_bps: float
    broker_shortfall_bps: float

    # Realistic Conservative Shadow Execution
    shadow_fill_price: float
    shadow_fill_ts: pd.Timestamp
    shadow_slippage_bps: float
    shadow_shortfall_bps: float

    @property
    def paper_fill_advantage_bps(self) -> float:
        """
        Paper Fill Optimism Metric:
        Positive means broker paper gave a better price than realistic conservative market observation.
        """
        return self.shadow_shortfall_bps - self.broker_shortfall_bps

    @property
    def paper_optimism_bps(self) -> float:
        return self.paper_fill_advantage_bps


@dataclass
class ReconciliationErrorRecord:
    timestamp: pd.Timestamp
    symbol: Optional[str]
    error_type: str  # "CASH_MISMATCH", "POSITION_QTY_MISMATCH", "AVG_PRICE_MISMATCH", "GHOST_ORDER"
    internal_value: Any
    broker_value: Any
    discrepancy: str
    resolved: bool = False


class DualExecutionLedger:
    """Maintains and compares simultaneous Broker Paper and Realistic Shadow books."""

    def __init__(self):
        self.comparisons: List[DualExecutionComparison] = []
        self._disabled_symbols: Set[str] = set()
        self.is_paused = False
        self.is_system_locked_out = False

    def record_dual_execution(self, comparison: DualExecutionComparison) -> None:
        self.comparisons.append(comparison)

    def record_comparison(self, comp: DualExecutionComparison) -> None:
        self.comparisons.append(comp)

    def compute_optimism_summary(self) -> Dict[str, Any]:
        """Compute aggregate paper fill advantage and breakdown by symbol and spread."""
        if not self.comparisons:
            return {
                "count": 0,
                "mean_paper_advantage_bps": 0.0,
                "median_paper_advantage_bps": 0.0,
                "p90_paper_advantage_bps": 0.0,
                "by_symbol": {},
            }

        advs = np.array([c.paper_fill_advantage_bps for c in self.comparisons])
        by_symbol = {}
        for sym in set(c.symbol for c in self.comparisons):
            sym_advs = [c.paper_fill_advantage_bps for c in self.comparisons if c.symbol == sym]
            by_symbol[sym] = {
                "count": len(sym_advs),
                "mean_advantage_bps": float(np.mean(sym_advs)),
                "median_advantage_bps": float(np.median(sym_advs)),
            }

        return {
            "count": len(self.comparisons),
            "mean_paper_advantage_bps": float(np.mean(advs)),
            "median_paper_advantage_bps": float(np.median(advs)),
            "p90_paper_advantage_bps": float(np.percentile(advs, 90)),
            "by_symbol": by_symbol,
        }

    def get_summary(self) -> Dict[str, Any]:
        return self.compute_optimism_summary()


class AccountReconciler:
    """
    Reconciles internal shadow state with broker source of truth.
    Freezes trading on discrepancies.
    """

    def __init__(
        self,
        broker: Any,
        internal_portfolio: Any,
        max_cash_tolerance_usd: float = 1.0,
        max_qty_tolerance: float = 1e-4,
    ):
        self.broker = broker
        self.internal = internal_portfolio
        self.max_cash_tolerance = max_cash_tolerance_usd
        self.max_qty_tolerance = max_qty_tolerance
        self.reconciliation_errors: List[ReconciliationErrorRecord] = []
        self.has_active_error = False

    def reconcile(self) -> Tuple[bool, List[ReconciliationErrorRecord]]:
        """
        Execute full cross-ledger reconciliation.
        Returns: (is_clean, list_of_errors)
        """
        errors = []
        now = pd.Timestamp.now(tz=timezone.utc)

        # 1. Fetch Broker Ground Truth
        try:
            broker_acc = self.broker.get_account()
            broker_positions = self.broker.get_positions()
        except Exception as e:
            err = ReconciliationErrorRecord(
                timestamp=now,
                symbol=None,
                error_type="BROKER_UNREACHABLE",
                internal_value="OK",
                broker_value=str(e),
                discrepancy=f"Broker query failed during reconciliation: {e}",
            )
            errors.append(err)
            self.reconciliation_errors.append(err)
            self.has_active_error = True
            return False, errors

        # 2. Reconcile Positions
        all_symbols = set(self.internal.positions.keys()).union(set(broker_positions.keys()))
        for sym in all_symbols:
            internal_pos = self.internal.positions.get(sym)
            broker_pos = broker_positions.get(sym)

            internal_qty = internal_pos.shares if internal_pos else 0.0
            broker_qty = broker_pos.qty if hasattr(broker_pos, "qty") else (broker_pos if isinstance(broker_pos, (int, float)) else 0.0)

            if abs(internal_qty - broker_qty) > self.max_qty_tolerance:
                err = ReconciliationErrorRecord(
                    timestamp=now,
                    symbol=sym,
                    error_type="POSITION_QTY_MISMATCH",
                    internal_value=internal_qty,
                    broker_value=broker_qty,
                    discrepancy=f"Position quantity mismatch on {sym}: Internal={internal_qty}, Broker={broker_qty}",
                )
                errors.append(err)

            if internal_pos and broker_pos and hasattr(broker_pos, "avg_entry_price"):
                price_diff = abs(internal_pos.entry_price - broker_pos.avg_entry_price)
                if price_diff > 0.05:  # $0.05 tolerance
                    err = ReconciliationErrorRecord(
                        timestamp=now,
                        symbol=sym,
                        error_type="AVG_PRICE_MISMATCH",
                        internal_value=internal_pos.entry_price,
                        broker_value=broker_pos.avg_entry_price,
                        discrepancy=f"Entry price mismatch on {sym}: Internal={internal_pos.entry_price:.2f}, Broker={broker_pos.avg_entry_price:.2f}",
                    )
                    errors.append(err)

        # 3. Reconcile Cash
        cash_diff = abs(self.internal.cash - broker_acc.cash)
        if cash_diff > self.max_cash_tolerance:
            err = ReconciliationErrorRecord(
                timestamp=now,
                symbol=None,
                error_type="CASH_MISMATCH",
                internal_value=self.internal.cash,
                broker_value=broker_acc.cash,
                discrepancy=f"Cash balance mismatch: Internal=${self.internal.cash:.2f}, Broker=${broker_acc.cash:.2f} (Diff: ${cash_diff:.2f})",
            )
            errors.append(err)

        if errors:
            self.reconciliation_errors.extend(errors)
            self.has_active_error = True
            return False, errors
        else:
            self.has_active_error = False
            return True, []

    def recover_from_broker_state(self) -> None:
        """
        Crash Recovery: Sync internal portfolio strictly from Broker Ground Truth.
        """
        broker_acc = self.broker.get_account()
        broker_positions = self.broker.get_positions()

        self.internal.cash = broker_acc.cash
        self.internal.positions.clear()

        from src.portfolio.shadow_portfolio import ShadowPosition
        for sym, pos in broker_positions.items():
            qty = pos.qty if hasattr(pos, "qty") else float(pos)
            price = pos.avg_entry_price if hasattr(pos, "avg_entry_price") else 100.0
            cur_p = pos.current_price if hasattr(pos, "current_price") else price

            self.internal.positions[sym] = ShadowPosition(
                symbol=sym,
                shares=qty,
                entry_price=price,
                entry_timestamp=pd.Timestamp.now(tz=timezone.utc),
                sector="Technology",
                current_price=cur_p,
                stop_loss_price=price * 0.985,
                take_profit_price=price * 1.030,
            )
        self.has_active_error = False


# ==============================================================================
# Phase F Modular Reconciliation Services
# ==============================================================================

class ReconciliationStatus(str, Enum):
    CLEAN = "CLEAN"
    WARNING = "WARNING"
    FAILED = "FAILED"


@dataclass
class ReconciliationReport:
    timestamp: str
    status: ReconciliationStatus
    unexplained_position_mismatches: List[str]
    unexplained_order_mismatches: List[str]
    is_safe_to_operate: bool
    details: Dict[str, Any]


class BrokerReconciliationService:
    """
    Performs deterministic reconciliation against broker state for Phase F runtime.
    """
    def __init__(self, broker: Any):
        self.broker = broker

    def reconcile(
        self,
        internal_positions: Dict[str, ManagedPosition],
        strategy_ledger: StrategyCapitalLedger,
    ) -> ReconciliationReport:
        t_now = datetime.now(timezone.utc).isoformat()
        mismatches: List[str] = []
        order_mismatches: List[str] = []

        try:
            broker_pos = self.broker.get_positions()
            broker_orders = self.broker.get_open_orders()

            all_syms = set(internal_positions.keys()).union(set(broker_pos.keys()))
            for sym in all_syms:
                int_shares = internal_positions[sym].shares if sym in internal_positions else 0
                brk_val = broker_pos.get(sym, 0.0)
                brk_shares = int(brk_val.qty if hasattr(brk_val, "qty") else brk_val)

                if int_shares != brk_shares:
                    mismatches.append(
                        f"POSITION_MISMATCH: {sym} internal={int_shares}, broker={brk_shares}"
                    )

            if len(broker_orders) > 0 and len(internal_positions) == 0:
                for o in broker_orders:
                    o_id = o.broker_order_id if hasattr(o, "broker_order_id") else (o.client_order_id if hasattr(o, "client_order_id") else "UNKNOWN")
                    order_mismatches.append(f"UNTRACKED_OPEN_ORDER: {o_id} for {getattr(o, 'symbol', 'UNKNOWN')}")

            is_clean = len(mismatches) == 0 and len(order_mismatches) == 0
            status = ReconciliationStatus.CLEAN if is_clean else ReconciliationStatus.FAILED

            return ReconciliationReport(
                timestamp=t_now,
                status=status,
                unexplained_position_mismatches=mismatches,
                unexplained_order_mismatches=order_mismatches,
                is_safe_to_operate=is_clean,
                details={
                    "internal_position_count": len(internal_positions),
                    "broker_position_count": len(broker_pos),
                    "open_order_count": len(broker_orders),
                }
            )
        except Exception as exc:
            logger.error("Reconciliation threw exception: %s", exc)
            return ReconciliationReport(
                timestamp=t_now,
                status=ReconciliationStatus.FAILED,
                unexplained_position_mismatches=[f"EXCEPTION: {str(exc)}"],
                unexplained_order_mismatches=[],
                is_safe_to_operate=False,
                details={"error": str(exc)},
            )
