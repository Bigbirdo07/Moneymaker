"""
Autonomous Entry Decision Model V1.1 (Calibrated Low-Turnover Engine).
Enforces high-conviction net edge gates, re-entry cooldown periods,
daily trade velocity caps, and tight liquidity filtering.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass, PortfolioState
from src.models.multi_horizon_forecaster import MultiHorizonPrediction

logger = get_logger("signals.entry_model_v1_1")


@dataclass
class EntryDecisionV1_1:
    """Decision output for an entry opportunity evaluation under V1.1 rules."""
    symbol: str
    timestamp: str
    action: str  # BUY, SKIP
    reason: str
    expected_gross_return_bps: float
    estimated_friction_bps: float
    expected_net_edge_bps: float
    probability_positive: float
    target_horizon_min: int
    confidence_score: float
    suggested_allocation_pct: float
    is_authorized: bool
    evidence_class: str = EvidenceClass.HISTORICAL_REPLAY.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EntryDecisionModelV1_1:
    """
    Calibrated V1.1 Entry Decision Engine.
    Filters out noise, prevents rapid oscillation, and trades strictly on institutional conviction.
    """

    def __init__(
        self,
        min_net_edge_bps: float = 10.0,
        min_probability_positive: float = 0.58,
        max_spread_bps: float = 10.0,
        max_position_allocation_pct: float = 0.33,
        re_entry_cooldown_bars: int = 30,
        max_daily_trades: int = 8,
        max_concurrent_positions: int = 3,
    ) -> None:
        self.min_net_edge_bps = min_net_edge_bps
        self.min_probability_positive = min_probability_positive
        self.max_spread_bps = max_spread_bps
        self.max_position_allocation_pct = max_position_allocation_pct
        self.re_entry_cooldown_bars = re_entry_cooldown_bars
        self.max_daily_trades = max_daily_trades
        self.max_concurrent_positions = max_concurrent_positions

        # State tracking for cooldowns and trade frequency
        self.last_exit_bar: Dict[str, int] = {}
        self.session_trade_count: int = 0
        self.current_session_date: Optional[str] = None

    def reset_session(self, session_date: str) -> None:
        """Resets session-level velocity counters at market open."""
        self.session_trade_count = 0
        self.current_session_date = session_date
        self.last_exit_bar.clear()

    def record_trade_executed(self) -> None:
        """Increments session trade execution counter."""
        self.session_trade_count += 1

    def record_symbol_exit(self, symbol: str, current_bar_index: int) -> None:
        """Records the bar index when a symbol position was closed for cooldown enforcement."""
        self.last_exit_bar[symbol] = current_bar_index

    def evaluate_entry(
        self,
        prediction: MultiHorizonPrediction,
        current_spread_bps: float,
        portfolio: PortfolioState,
        current_bar_index: int = 0,
        minutes_to_close: float = 390.0,
        market_regime: str = "NORMAL",
    ) -> EntryDecisionV1_1:
        """
        Evaluates candidate entry under V1.1 rules.
        """
        opt_h = prediction.optimal_target_horizon_min
        forecast = getattr(prediction, f"forecast_{opt_h}m", prediction.forecast_15m)

        net_edge = forecast.expected_net_return_bps
        p_up = forecast.probability_positive
        conf = forecast.confidence

        # 1. Daily Trade Frequency Cap
        if self.session_trade_count >= self.max_daily_trades:
            return EntryDecisionV1_1(
                symbol=prediction.symbol,
                timestamp=prediction.timestamp,
                action="SKIP",
                reason="DAILY_TRADE_LIMIT_REACHED",
                expected_gross_return_bps=forecast.expected_return_bps,
                estimated_friction_bps=forecast.estimated_friction_bps,
                expected_net_edge_bps=net_edge,
                probability_positive=p_up,
                target_horizon_min=opt_h,
                confidence_score=conf,
                suggested_allocation_pct=0.0,
                is_authorized=False,
            )

        # 2. Max Concurrent Open Positions Cap
        if len(portfolio.positions) >= self.max_concurrent_positions:
            return EntryDecisionV1_1(
                symbol=prediction.symbol,
                timestamp=prediction.timestamp,
                action="SKIP",
                reason="MAX_CONCURRENT_POSITIONS_REACHED",
                expected_gross_return_bps=forecast.expected_return_bps,
                estimated_friction_bps=forecast.estimated_friction_bps,
                expected_net_edge_bps=net_edge,
                probability_positive=p_up,
                target_horizon_min=opt_h,
                confidence_score=conf,
                suggested_allocation_pct=0.0,
                is_authorized=False,
            )

        # 3. Session End / Open Proximity Buffers
        if minutes_to_close <= 30.0:
            return EntryDecisionV1_1(
                symbol=prediction.symbol,
                timestamp=prediction.timestamp,
                action="SKIP",
                reason="SESSION_CLOSE_PROXIMITY",
                expected_gross_return_bps=forecast.expected_return_bps,
                estimated_friction_bps=forecast.estimated_friction_bps,
                expected_net_edge_bps=net_edge,
                probability_positive=p_up,
                target_horizon_min=opt_h,
                confidence_score=conf,
                suggested_allocation_pct=0.0,
                is_authorized=False,
            )

        # 4. Symbol Re-Entry Cooldown Period
        if prediction.symbol in self.last_exit_bar:
            bars_since_exit = current_bar_index - self.last_exit_bar[prediction.symbol]
            if 0 <= bars_since_exit < self.re_entry_cooldown_bars:
                return EntryDecisionV1_1(
                    symbol=prediction.symbol,
                    timestamp=prediction.timestamp,
                    action="SKIP",
                    reason=f"RE_ENTRY_COOLDOWN_ACTIVE_{bars_since_exit}_OF_{self.re_entry_cooldown_bars}_BARS",
                    expected_gross_return_bps=forecast.expected_return_bps,
                    estimated_friction_bps=forecast.estimated_friction_bps,
                    expected_net_edge_bps=net_edge,
                    probability_positive=p_up,
                    target_horizon_min=opt_h,
                    confidence_score=conf,
                    suggested_allocation_pct=0.0,
                    is_authorized=False,
                )

        # 5. Spread Friction Gate
        if current_spread_bps > self.max_spread_bps:
            return EntryDecisionV1_1(
                symbol=prediction.symbol,
                timestamp=prediction.timestamp,
                action="SKIP",
                reason="EXCESSIVE_SPREAD_FRICTION",
                expected_gross_return_bps=forecast.expected_return_bps,
                estimated_friction_bps=forecast.estimated_friction_bps,
                expected_net_edge_bps=net_edge,
                probability_positive=p_up,
                target_horizon_min=opt_h,
                confidence_score=conf,
                suggested_allocation_pct=0.0,
                is_authorized=False,
            )

        # 6. Available Cash Constraint
        if portfolio.cash < (portfolio.portfolio_value * 0.10):
            return EntryDecisionV1_1(
                symbol=prediction.symbol,
                timestamp=prediction.timestamp,
                action="SKIP",
                reason="INSUFFICIENT_AVAILABLE_CASH",
                expected_gross_return_bps=forecast.expected_return_bps,
                estimated_friction_bps=forecast.estimated_friction_bps,
                expected_net_edge_bps=net_edge,
                probability_positive=p_up,
                target_horizon_min=opt_h,
                confidence_score=conf,
                suggested_allocation_pct=0.0,
                is_authorized=False,
            )

        # 7. High-Conviction Edge & Probability Hurdle
        if net_edge >= self.min_net_edge_bps and p_up >= self.min_probability_positive:
            alloc_pct = min(self.max_position_allocation_pct, round(0.20 + (conf * 0.13), 3))
            return EntryDecisionV1_1(
                symbol=prediction.symbol,
                timestamp=prediction.timestamp,
                action="BUY",
                reason="HIGH_CONVICTION_EDGE_CONFIRMED",
                expected_gross_return_bps=forecast.expected_return_bps,
                estimated_friction_bps=forecast.estimated_friction_bps,
                expected_net_edge_bps=net_edge,
                probability_positive=p_up,
                target_horizon_min=opt_h,
                confidence_score=conf,
                suggested_allocation_pct=alloc_pct,
                is_authorized=True,
            )

        return EntryDecisionV1_1(
            symbol=prediction.symbol,
            timestamp=prediction.timestamp,
            action="SKIP",
            reason="SUB_THRESHOLD_EDGE_OR_PROBABILITY",
            expected_gross_return_bps=forecast.expected_return_bps,
            estimated_friction_bps=forecast.estimated_friction_bps,
            expected_net_edge_bps=net_edge,
            probability_positive=p_up,
            target_horizon_min=opt_h,
            confidence_score=conf,
            suggested_allocation_pct=0.0,
            is_authorized=False,
        )
