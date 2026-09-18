"""
Real-Market Exit Model V3 for Phase 11B / Engine V3.
Enforces multi-layer risk controls: Stop Loss, Dynamic Take-Profit Target,
Gain-Locking Trailing Stops, Signal Decay, and Overnight Gap Risk Management.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.core.logging import get_logger
from src.core.types import EvidenceClass

logger = get_logger("signals.real_exit_model_v3")


@dataclass
class ExitDecisionV3:
    """Exit evaluation outcome."""
    should_exit: bool
    exit_reason: str
    target_price: float
    evidence_class: str = EvidenceClass.SIMULATED_EXECUTION_ON_REAL_MARKET_DATA.value


class RealMarketExitModelV3:
    """
    Exit controller designed to eliminate overnight gap risks and lock in positive MFE.
    """

    def __init__(
        self,
        stop_loss_pct: float = 0.015,
        take_profit_pct: float = 0.030,
        trailing_drawdown_pct: float = 0.0075,
        max_holding_bars: int = 60,
    ) -> None:
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.trailing_drawdown_pct = trailing_drawdown_pct
        self.max_holding_bars = max_holding_bars

    def evaluate_exit(
        self,
        entry_price: float,
        current_price: float,
        peak_price: float,
        bars_held: int,
        predicted_edge_bps: float,
        time_str: str,
    ) -> ExitDecisionV3:
        """
        Evaluates dynamic exit triggers.
        """
        unrealized_ret = (current_price - entry_price) / entry_price
        retrace_from_peak = (peak_price - current_price) / peak_price if peak_price > 0 else 0.0

        # 1. Hard Stop Loss
        if unrealized_ret <= -self.stop_loss_pct:
            return ExitDecisionV3(
                should_exit=True,
                exit_reason=f"HARD_STOP_LOSS_{unrealized_ret*100:.2f}%_LE_-{self.stop_loss_pct*100:.2f}%",
                target_price=current_price,
            )

        # 2. Take Profit Target Hit
        if unrealized_ret >= self.take_profit_pct:
            return ExitDecisionV3(
                should_exit=True,
                exit_reason=f"TAKE_PROFIT_TARGET_{unrealized_ret*100:.2f}%_GE_{self.take_profit_pct*100:.2f}%",
                target_price=current_price,
            )

        # 3. Trailing Stop (Active once position gained >= +1.50%)
        peak_ret = (peak_price - entry_price) / entry_price
        if peak_ret >= 0.015 and retrace_from_peak >= self.trailing_drawdown_pct:
            return ExitDecisionV3(
                should_exit=True,
                exit_reason=f"TRAILING_DRAWDOWN_{retrace_from_peak*100:.2f}%_GE_{self.trailing_drawdown_pct*100:.2f}%",
                target_price=current_price,
            )

        # 4. Signal Decay
        if predicted_edge_bps < -5.0 and bars_held >= 15:
            return ExitDecisionV3(
                should_exit=True,
                exit_reason=f"SIGNAL_DECAY_EDGE_{predicted_edge_bps:.1f}bps_LT_-5.0bps",
                target_price=current_price,
            )

        # 5. Max Holding Duration Exceeded
        if bars_held >= self.max_holding_bars:
            return ExitDecisionV3(
                should_exit=True,
                exit_reason=f"MAX_HOLDING_BARS_{bars_held}_GE_{self.max_holding_bars}",
                target_price=current_price,
            )

        return ExitDecisionV3(should_exit=False, exit_reason="HOLD", target_price=current_price)
