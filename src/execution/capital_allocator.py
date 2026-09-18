"""
Autonomous Capital Allocator for $1,000 Starting Account.
Enforces whole-share constraints, maximum portfolio exposure limits,
and deterministic risk boundaries with full 100% Cash capability.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
import numpy as np

from src.core.logging import get_logger
from src.core.types import EvidenceClass, PortfolioState
from src.signals.entry_model import EntryDecision

logger = get_logger("execution.capital_allocator")


@dataclass
class AllocationTarget:
    """Target capital allocation for an individual opportunity."""
    symbol: str
    target_dollars: float
    target_shares: int
    expected_edge_bps: float
    risk_score: float
    allocation_pct: float
    estimated_friction_dollars: float
    is_cash: bool = False
    evidence_class: str = EvidenceClass.HISTORICAL_REPLAY.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PortfolioAllocationPlan:
    """Complete portfolio allocation plan across universe at timestamp T."""
    timestamp: str
    total_capital: float
    available_cash: float
    allocated_dollars: float
    unallocated_cash_dollars: float
    targets: List[AllocationTarget]
    target_portfolio_exposure_pct: float
    is_fully_cash: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "total_capital": self.total_capital,
            "available_cash": self.available_cash,
            "allocated_dollars": self.allocated_dollars,
            "unallocated_cash_dollars": self.unallocated_cash_dollars,
            "targets": [t.to_dict() for t in self.targets],
            "target_portfolio_exposure_pct": self.target_portfolio_exposure_pct,
            "is_fully_cash": self.is_fully_cash,
        }


class AutonomousCapitalAllocator:
    """
    Allocates capital across authorized opportunities for a $1,000 account.
    """

    def __init__(
        self,
        max_position_pct: float = 0.25,        # Max $250 on $1,000 account
        max_portfolio_exposure_pct: float = 0.80, # Max $800 total active equity
        max_active_positions: int = 4,
        allow_fractional_shares: bool = False,
        min_order_dollars: float = 25.0,
    ) -> None:
        self.max_position_pct = max_position_pct
        self.max_portfolio_exposure_pct = max_portfolio_exposure_pct
        self.max_active_positions = max_active_positions
        self.allow_fractional_shares = allow_fractional_shares
        self.min_order_dollars = min_order_dollars

    def allocate(
        self,
        timestamp: str,
        portfolio: PortfolioState,
        candidate_entries: List[Tuple[EntryDecision, float]],  # (decision, current_price)
    ) -> PortfolioAllocationPlan:
        """
        Creates allocation plan for candidate opportunities given current portfolio state.
        """
        total_equity = portfolio.portfolio_value
        available_cash = portfolio.cash
        current_active_count = len(portfolio.positions)

        # Slots remaining
        open_slots = max(0, self.max_active_positions - current_active_count)
        if open_slots == 0 or not candidate_entries or available_cash < self.min_order_dollars:
            return PortfolioAllocationPlan(
                timestamp=timestamp,
                total_capital=round(total_equity, 2),
                available_cash=round(available_cash, 2),
                allocated_dollars=0.0,
                unallocated_cash_dollars=round(available_cash, 2),
                targets=[],
                target_portfolio_exposure_pct=round((total_equity - available_cash) / total_equity if total_equity > 0 else 0, 4),
                is_fully_cash=(len(portfolio.positions) == 0),
            )

        # Filter to authorized BUY decisions not currently held
        valid_candidates = [
            (d, price) for (d, price) in candidate_entries
            if d.action == "BUY" and d.is_authorized and d.symbol not in portfolio.positions and price > 0
        ]

        if not valid_candidates:
            return PortfolioAllocationPlan(
                timestamp=timestamp,
                total_capital=round(total_equity, 2),
                available_cash=round(available_cash, 2),
                allocated_dollars=0.0,
                unallocated_cash_dollars=round(available_cash, 2),
                targets=[],
                target_portfolio_exposure_pct=round((total_equity - available_cash) / total_equity if total_equity > 0 else 0, 4),
                is_fully_cash=(len(portfolio.positions) == 0),
            )

        # Sort by expected net edge descending
        valid_candidates.sort(key=lambda x: x[0].expected_net_edge_bps, reverse=True)
        selected = valid_candidates[:open_slots]

        targets: List[AllocationTarget] = []
        remaining_cash = available_cash
        current_invested = total_equity - available_cash

        for decision, price in selected:
            # Check maximum exposure constraint
            max_allowed_invested = total_equity * self.max_portfolio_exposure_pct
            investable_headroom = max(0.0, max_allowed_invested - current_invested)
            if investable_headroom < self.min_order_dollars or remaining_cash < self.min_order_dollars:
                break

            # Calculate target dollars
            desired_pct = min(self.max_position_pct, decision.suggested_allocation_pct)
            desired_dollars = total_equity * desired_pct
            target_dollars = min(desired_dollars, remaining_cash, investable_headroom)

            if target_dollars < self.min_order_dollars:
                continue

            # Calculate shares
            if self.allow_fractional_shares:
                shares = round(target_dollars / price, 4)
                actual_dollars = round(shares * price, 2)
            else:
                shares = int(target_dollars // price)
                actual_dollars = round(shares * price, 2)

            if shares <= 0 or actual_dollars < self.min_order_dollars:
                continue

            friction_est = round((actual_dollars * (decision.estimated_friction_bps / 10000.0)) + 0.005, 4)

            target = AllocationTarget(
                symbol=decision.symbol,
                target_dollars=actual_dollars,
                target_shares=shares,
                expected_edge_bps=decision.expected_net_edge_bps,
                risk_score=round(1.0 - decision.confidence_score, 3),
                allocation_pct=round(actual_dollars / total_equity, 4),
                estimated_friction_dollars=friction_est,
                is_cash=False,
            )
            targets.append(target)
            remaining_cash -= actual_dollars
            current_invested += actual_dollars

        total_alloc = sum(t.target_dollars for t in targets)
        is_cash_all = (len(portfolio.positions) == 0 and len(targets) == 0)

        return PortfolioAllocationPlan(
            timestamp=timestamp,
            total_capital=round(total_equity, 2),
            available_cash=round(available_cash, 2),
            allocated_dollars=round(total_alloc, 2),
            unallocated_cash_dollars=round(remaining_cash, 2),
            targets=targets,
            target_portfolio_exposure_pct=round((current_invested) / total_equity if total_equity > 0 else 0, 4),
            is_fully_cash=is_cash_all,
        )
