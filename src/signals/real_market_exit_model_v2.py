"""
Real-Market Exit Decision Model V2 for Phase 10.4.
Enforces dynamic continuation value logic, multi-horizon signal decay tracking,
hard stop early-exit safety, and economically sound opportunity switching margins.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass

logger = get_logger("signals.real_exit_model_v2")


@dataclass
class ExitDecisionV2:
    """Decision output for an active position evaluation under V2 rules."""
    symbol: str
    timestamp: str
    action: str  # HOLD, SELL, REDUCE
    reason: str
    unrealized_pnl_pct: float
    bars_held: int
    current_continuation_edge_bps: float
    is_authorized_exit: bool
    evidence_class: str = EvidenceClass.REAL_HISTORICAL_MARKET_DATA.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RealMarketExitModelV2:
    """
    V2 Exit Decision Model calibrated for real market dynamics.
    """

    def __init__(
        self,
        stop_loss_pct: float = 0.015,         # 1.5% Hard Stop
        take_profit_pct: float = 0.030,       # 3.0% Profit Target
        trailing_drawdown_pct: float = 0.008, # 0.8% Trailing Drawdown from Peak
        max_holding_bars: int = 90,           # 90-minute Max Time Stop
        min_continuation_edge_bps: float = -3.0,
        switching_margin_bps: float = 25.0,
    ) -> None:
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.trailing_drawdown_pct = trailing_drawdown_pct
        self.max_holding_bars = max_holding_bars
        self.min_continuation_edge_bps = min_continuation_edge_bps
        self.switching_margin_bps = switching_margin_bps

    def evaluate_exit(
        self,
        symbol: str,
        timestamp: str,
        entry_price: float,
        current_price: float,
        high_price: float,
        low_price: float,
        bars_held: int,
        target_horizon_bars: int,
        current_continuation_edge_bps: float,
        time_str: str,
    ) -> ExitDecisionV2:
        """
        Evaluates active position under V2 exit rules.
        """
        pnl_pct = (current_price - entry_price) / entry_price
        drawdown_from_high = (high_price - current_price) / high_price if high_price > 0 else 0.0

        # 1. Hard Stop Loss (Early Exit Safety Override)
        if pnl_pct <= -self.stop_loss_pct:
            return ExitDecisionV2(
                symbol=symbol,
                timestamp=timestamp,
                action="SELL",
                reason=f"HARD_STOP_LOSS_{pnl_pct*100:.2f}%_LE_{-self.stop_loss_pct*100:.2f}%",
                unrealized_pnl_pct=round(pnl_pct, 4),
                bars_held=bars_held,
                current_continuation_edge_bps=round(current_continuation_edge_bps, 2),
                is_authorized_exit=True,
            )

        # 2. Take Profit Target
        if pnl_pct >= self.take_profit_pct:
            return ExitDecisionV2(
                symbol=symbol,
                timestamp=timestamp,
                action="SELL",
                reason=f"TAKE_PROFIT_TARGET_{pnl_pct*100:.2f}%_GE_{self.take_profit_pct*100:.2f}%",
                unrealized_pnl_pct=round(pnl_pct, 4),
                bars_held=bars_held,
                current_continuation_edge_bps=round(current_continuation_edge_bps, 2),
                is_authorized_exit=True,
            )

        # 3. Trailing Drawdown Lock (Protects gained alpha)
        if high_price >= entry_price * 1.012 and drawdown_from_high >= self.trailing_drawdown_pct:
            return ExitDecisionV2(
                symbol=symbol,
                timestamp=timestamp,
                action="SELL",
                reason=f"TRAILING_DRAWDOWN_{drawdown_from_high*100:.2f}%_GE_{self.trailing_drawdown_pct*100:.2f}%",
                unrealized_pnl_pct=round(pnl_pct, 4),
                bars_held=bars_held,
                current_continuation_edge_bps=round(current_continuation_edge_bps, 2),
                is_authorized_exit=True,
            )

        # 4. End of Day / Session Close Approach
        if time_str >= "15:55:00":
            return ExitDecisionV2(
                symbol=symbol,
                timestamp=timestamp,
                action="SELL",
                reason="SESSION_CLOSE_FLATTEN",
                unrealized_pnl_pct=round(pnl_pct, 4),
                bars_held=bars_held,
                current_continuation_edge_bps=round(current_continuation_edge_bps, 2),
                is_authorized_exit=True,
            )

        # 5. Max Holding Duration Exceeded
        if bars_held >= self.max_holding_bars:
            return ExitDecisionV2(
                symbol=symbol,
                timestamp=timestamp,
                action="SELL",
                reason=f"MAX_HOLDING_TIME_{bars_held}_GE_{self.max_holding_bars}_BARS",
                unrealized_pnl_pct=round(pnl_pct, 4),
                bars_held=bars_held,
                current_continuation_edge_bps=round(current_continuation_edge_bps, 2),
                is_authorized_exit=True,
            )

        # 6. Dynamic Signal Decay Exit (only after minimum holding threshold of target horizon / 2)
        min_bars_before_decay_exit = max(10, target_horizon_bars // 2)
        if bars_held >= min_bars_before_decay_exit:
            if current_continuation_edge_bps < self.min_continuation_edge_bps:
                return ExitDecisionV2(
                    symbol=symbol,
                    timestamp=timestamp,
                    action="SELL",
                    reason=f"SIGNAL_DECAY_EDGE_{current_continuation_edge_bps:.1f}bps_LT_{self.min_continuation_edge_bps:.1f}bps",
                    unrealized_pnl_pct=round(pnl_pct, 4),
                    bars_held=bars_held,
                    current_continuation_edge_bps=round(current_continuation_edge_bps, 2),
                    is_authorized_exit=True,
                )

        # Default HOLD Decision
        return ExitDecisionV2(
            symbol=symbol,
            timestamp=timestamp,
            action="HOLD",
            reason="CONTINUATION_VALUE_POSITIVE",
            unrealized_pnl_pct=round(pnl_pct, 4),
            bars_held=bars_held,
            current_continuation_edge_bps=round(current_continuation_edge_bps, 2),
            is_authorized_exit=False,
        )
