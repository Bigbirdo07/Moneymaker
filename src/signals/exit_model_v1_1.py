"""
Autonomous Exit Decision Model V1.1 (Calibrated Noise-Resistant Engine).
Protects alpha horizon by requiring minimum holding durations before signal decay,
raises opportunity switching barriers to prevent intraday churn, and trails profitable excursions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
import numpy as np

from src.core.logging import get_logger
from src.core.types import EvidenceClass, Position
from src.models.multi_horizon_forecaster import MultiHorizonPrediction

logger = get_logger("signals.exit_model_v1_1")


@dataclass
class ExitDecisionV1_1:
    """Decision output for open position evaluation under V1.1 rules."""
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
    reduce_fraction: float = 0.0
    evidence_class: str = EvidenceClass.HISTORICAL_REPLAY.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExitDecisionModelV1_1:
    """
    Noise-resistant exit decision model designed to allow alpha to mature
    across its empirical 15m/30m forecast horizon while cutting true catastrophic risk.
    """

    def __init__(
        self,
        stop_loss_pct: float = 0.015,
        take_profit_pct: float = 0.025,
        max_holding_bars: int = 90,
        trailing_drawdown_pct: float = 0.008,
        min_continuation_edge_bps: float = -4.0,
        opportunity_switch_margin_bps: float = 25.0,
        min_holding_bars_for_signal_decay: int = 15,
    ) -> None:
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_holding_bars = max_holding_bars
        self.trailing_drawdown_pct = trailing_drawdown_pct
        self.min_continuation_edge_bps = min_continuation_edge_bps
        self.opportunity_switch_margin_bps = opportunity_switch_margin_bps
        self.min_holding_bars_for_signal_decay = min_holding_bars_for_signal_decay

    def evaluate_exit(
        self,
        position: Position,
        current_price: float,
        prediction: MultiHorizonPrediction,
        minutes_to_close: float,
        best_competing_edge_bps: float = 0.0,
        high_water_mark: Optional[float] = None,
        low_water_mark: Optional[float] = None,
    ) -> ExitDecisionV1_1:
        """
        Evaluates open position at timestamp T with noise filtering and horizon protection.
        """
        entry_price = position.avg_entry_price
        ret = (current_price - entry_price) / entry_price
        ret_bps = ret * 10000.0

        peak = high_water_mark or max(entry_price, current_price)
        trough = low_water_mark or min(entry_price, current_price)
        mfe_bps = ((peak - entry_price) / entry_price) * 10000.0
        mae_bps = ((trough - entry_price) / entry_price) * 10000.0

        dd_from_peak = ((peak - current_price) / peak) if peak > 0 else 0.0
        dd_from_peak_bps = dd_from_peak * 10000.0

        current_edge = prediction.composite_net_edge_bps
        bars_held = position.bars_held

        # 1. Session Close Liquidation (Last 10 minutes)
        if minutes_to_close <= 10.0:
            return ExitDecisionV1_1(
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

        # 2. Hard Stop Loss (Always active for risk management)
        if ret <= -self.stop_loss_pct:
            return ExitDecisionV1_1(
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
            return ExitDecisionV1_1(
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

        # 4. Trailing Drawdown from Peak (Only when trade was in substantial profit > 40 bps)
        if mfe_bps >= 40.0 and dd_from_peak >= self.trailing_drawdown_pct:
            return ExitDecisionV1_1(
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

        # 5. Opportunity Cost Switching (Substantially higher hurdle: >= 25 bps)
        replacement_adv = best_competing_edge_bps - current_edge
        if replacement_adv >= self.opportunity_switch_margin_bps:
            return ExitDecisionV1_1(
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

        # 6. Horizon-Protected Signal Decay: ONLY trigger if held >= min_holding_bars_for_signal_decay
        if bars_held >= self.min_holding_bars_for_signal_decay and current_edge < self.min_continuation_edge_bps:
            return ExitDecisionV1_1(
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
            return ExitDecisionV1_1(
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

        # Default: Hold Continuation
        return ExitDecisionV1_1(
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
