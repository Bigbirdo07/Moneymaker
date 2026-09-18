"""
Autonomous Exit Decision Model & Decision Dataset Construction.
Evaluates open positions across signal decay, multi-horizon return forecasts,
unrealized P&L, MFE/MAE excursions, and cross-asset opportunity costs to emit HOLD, REDUCE, or SELL.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass, Position
from src.models.multi_horizon_forecaster import MultiHorizonPrediction

logger = get_logger("signals.exit_model")


@dataclass
class ExitDecision:
    """Decision output for an open position evaluation."""
    symbol: str
    timestamp: str
    action: str  # HOLD, REDUCE, SELL
    reason_category: str  # STOP_LOSS, TAKE_PROFIT, SIGNAL_DECAY, BETTER_OPPORTUNITY, SESSION_CLOSE, TIME_STOP, DRAWDOWN_FROM_PEAK, HOLD_CONTINUATION
    unrealized_pnl_bps: float
    bars_held: int
    current_edge_bps: float
    mfe_bps: float
    mae_bps: float
    drawdown_from_peak_bps: float
    replacement_advantage_bps: float
    is_exit_triggered: bool
    reduce_fraction: float = 0.0  # 1.0 for full sell, 0.5 for reduce, 0.0 for hold
    evidence_class: str = EvidenceClass.HISTORICAL_REPLAY.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExitDecisionModel:
    """
    Multi-factor exit decision model evaluating continuation edge vs. opportunity cost and risk.
    """

    def __init__(
        self,
        stop_loss_pct: float = 0.015,         # 1.5% fixed stop loss
        take_profit_pct: float = 0.025,       # 2.5% take profit target
        max_holding_bars: int = 120,          # 120 minutes max hold
        trailing_drawdown_pct: float = 0.008, # 0.8% retracement from peak MFE triggers exit
        min_continuation_edge_bps: float = -2.0, # Negative expected return after friction triggers signal decay exit
        opportunity_switch_margin_bps: float = 12.0, # Excess net edge required to switch positions
    ) -> None:
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_holding_bars = max_holding_bars
        self.trailing_drawdown_pct = trailing_drawdown_pct
        self.min_continuation_edge_bps = min_continuation_edge_bps
        self.opportunity_switch_margin_bps = opportunity_switch_margin_bps

    def evaluate_exit(
        self,
        position: Position,
        current_price: float,
        prediction: MultiHorizonPrediction,
        minutes_to_close: float,
        best_competing_edge_bps: float = 0.0,
        high_water_mark: Optional[float] = None,
        low_water_mark: Optional[float] = None,
    ) -> ExitDecision:
        """
        Evaluates open position at timestamp T.
        """
        entry_price = position.avg_entry_price
        ret = (current_price - entry_price) / entry_price
        ret_bps = ret * 10000.0

        # Update MFE and MAE
        peak = high_water_mark or max(entry_price, current_price)
        trough = low_water_mark or min(entry_price, current_price)
        mfe_bps = ((peak - entry_price) / entry_price) * 10000.0
        mae_bps = ((trough - entry_price) / entry_price) * 10000.0

        dd_from_peak = ((peak - current_price) / peak) if peak > 0 else 0.0
        dd_from_peak_bps = dd_from_peak * 10000.0

        current_edge = prediction.composite_net_edge_bps
        bars_held = position.bars_held

        # 1. End of day forced liquidation (last 10 minutes)
        if minutes_to_close <= 10.0:
            return ExitDecision(
                symbol=position.symbol,
                timestamp=prediction.timestamp,
                action="SELL",
                reason_category="SESSION_CLOSE",
                unrealized_pnl_bps=round(ret_bps, 2),
                bars_held=bars_held,
                current_edge_bps=round(current_edge, 2),
                mfe_bps=round(mfe_bps, 2),
                mae_bps=round(mae_bps, 2),
                drawdown_from_peak_bps=round(dd_from_peak_bps, 2),
                replacement_advantage_bps=0.0,
                is_exit_triggered=True,
                reduce_fraction=1.0,
            )

        # 2. Hard Stop Loss
        if ret <= -self.stop_loss_pct:
            return ExitDecision(
                symbol=position.symbol,
                timestamp=prediction.timestamp,
                action="SELL",
                reason_category="STOP_LOSS",
                unrealized_pnl_bps=round(ret_bps, 2),
                bars_held=bars_held,
                current_edge_bps=round(current_edge, 2),
                mfe_bps=round(mfe_bps, 2),
                mae_bps=round(mae_bps, 2),
                drawdown_from_peak_bps=round(dd_from_peak_bps, 2),
                replacement_advantage_bps=0.0,
                is_exit_triggered=True,
                reduce_fraction=1.0,
            )

        # 3. Take Profit Target
        if ret >= self.take_profit_pct:
            return ExitDecision(
                symbol=position.symbol,
                timestamp=prediction.timestamp,
                action="SELL",
                reason_category="TAKE_PROFIT",
                unrealized_pnl_bps=round(ret_bps, 2),
                bars_held=bars_held,
                current_edge_bps=round(current_edge, 2),
                mfe_bps=round(mfe_bps, 2),
                mae_bps=round(mae_bps, 2),
                drawdown_from_peak_bps=round(dd_from_peak_bps, 2),
                replacement_advantage_bps=0.0,
                is_exit_triggered=True,
                reduce_fraction=1.0,
            )

        # 4. Trailing Drawdown from Local Peak (Protect gains if MFE was significant)
        if mfe_bps >= 50.0 and dd_from_peak >= self.trailing_drawdown_pct:
            return ExitDecision(
                symbol=position.symbol,
                timestamp=prediction.timestamp,
                action="SELL",
                reason_category="DRAWDOWN_FROM_PEAK",
                unrealized_pnl_bps=round(ret_bps, 2),
                bars_held=bars_held,
                current_edge_bps=round(current_edge, 2),
                mfe_bps=round(mfe_bps, 2),
                mae_bps=round(mae_bps, 2),
                drawdown_from_peak_bps=round(dd_from_peak_bps, 2),
                replacement_advantage_bps=0.0,
                is_exit_triggered=True,
                reduce_fraction=1.0,
            )

        # 5. Opportunity Cost Switching (Substantially better competing opportunity exists)
        replacement_adv = best_competing_edge_bps - current_edge
        if replacement_adv >= self.opportunity_switch_margin_bps:
            return ExitDecision(
                symbol=position.symbol,
                timestamp=prediction.timestamp,
                action="SELL",
                reason_category="BETTER_OPPORTUNITY",
                unrealized_pnl_bps=round(ret_bps, 2),
                bars_held=bars_held,
                current_edge_bps=round(current_edge, 2),
                mfe_bps=round(mfe_bps, 2),
                mae_bps=round(mae_bps, 2),
                drawdown_from_peak_bps=round(dd_from_peak_bps, 2),
                replacement_advantage_bps=round(replacement_adv, 2),
                is_exit_triggered=True,
                reduce_fraction=1.0,
            )

        # 6. Signal Decay
        if current_edge < self.min_continuation_edge_bps:
            return ExitDecision(
                symbol=position.symbol,
                timestamp=prediction.timestamp,
                action="SELL",
                reason_category="SIGNAL_DECAY",
                unrealized_pnl_bps=round(ret_bps, 2),
                bars_held=bars_held,
                current_edge_bps=round(current_edge, 2),
                mfe_bps=round(mfe_bps, 2),
                mae_bps=round(mae_bps, 2),
                drawdown_from_peak_bps=round(dd_from_peak_bps, 2),
                replacement_advantage_bps=0.0,
                is_exit_triggered=True,
                reduce_fraction=1.0,
            )

        # 7. Max Holding Duration Expired
        if bars_held >= self.max_holding_bars:
            return ExitDecision(
                symbol=position.symbol,
                timestamp=prediction.timestamp,
                action="SELL",
                reason_category="TIME_STOP",
                unrealized_pnl_bps=round(ret_bps, 2),
                bars_held=bars_held,
                current_edge_bps=round(current_edge, 2),
                mfe_bps=round(mfe_bps, 2),
                mae_bps=round(mae_bps, 2),
                drawdown_from_peak_bps=round(dd_from_peak_bps, 2),
                replacement_advantage_bps=0.0,
                is_exit_triggered=True,
                reduce_fraction=1.0,
            )

        # Default: Continue Holding
        return ExitDecision(
            symbol=position.symbol,
            timestamp=prediction.timestamp,
            action="HOLD",
            reason_category="HOLD_CONTINUATION",
            unrealized_pnl_bps=round(ret_bps, 2),
            bars_held=bars_held,
            current_edge_bps=round(current_edge, 2),
            mfe_bps=round(mfe_bps, 2),
            mae_bps=round(mae_bps, 2),
            drawdown_from_peak_bps=round(dd_from_peak_bps, 2),
            replacement_advantage_bps=round(replacement_adv, 2),
            is_exit_triggered=False,
            reduce_fraction=0.0,
        )
