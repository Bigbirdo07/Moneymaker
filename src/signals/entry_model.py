"""
Autonomous Entry Decision Model for Historical Replay & Live Simulation.
Evaluates candidate net edge, liquidity, and portfolio constraints to emit BUY or SKIP.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass, PortfolioState
from src.models.multi_horizon_forecaster import MultiHorizonPrediction

logger = get_logger("signals.entry_model")


@dataclass
class EntryDecision:
    """Decision output for an entry opportunity evaluation."""
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


class EntryDecisionModel:
    """
    Evaluates whether an opportunity warrants capital commitment by enforcing
    strict net edge, liquidity, friction, and portfolio exposure criteria.
    """

    def __init__(
        self,
        min_net_edge_bps: float = 4.0,
        min_probability_positive: float = 0.53,
        max_spread_bps: float = 15.0,
        max_position_allocation_pct: float = 0.25,
    ) -> None:
        self.min_net_edge_bps = min_net_edge_bps
        self.min_probability_positive = min_probability_positive
        self.max_spread_bps = max_spread_bps
        self.max_position_allocation_pct = max_position_allocation_pct

    def evaluate_entry(
        self,
        prediction: MultiHorizonPrediction,
        current_spread_bps: float,
        portfolio: PortfolioState,
        minutes_to_close: float = 390.0,
        market_regime: str = "NORMAL",
    ) -> EntryDecision:
        """
        Evaluates an individual asset's prediction at timestamp T to decide BUY or SKIP.
        """
        opt_h = prediction.optimal_target_horizon_min
        forecast = getattr(prediction, f"forecast_{opt_h}m", prediction.forecast_15m)

        net_edge = forecast.expected_net_return_bps
        p_up = forecast.probability_positive
        conf = forecast.confidence

        # Rejection conditions
        if minutes_to_close <= 20.0:
            return EntryDecision(
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

        if current_spread_bps > self.max_spread_bps:
            return EntryDecision(
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

        if portfolio.cash < (portfolio.portfolio_value * 0.05):
            return EntryDecision(
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

        # Edge & Probability Gate
        if net_edge >= self.min_net_edge_bps and p_up >= self.min_probability_positive:
            # Scale allocation with confidence
            alloc_pct = min(self.max_position_allocation_pct, round(0.10 + (conf * 0.15), 3))
            return EntryDecision(
                symbol=prediction.symbol,
                timestamp=prediction.timestamp,
                action="BUY",
                reason="POSITIVE_NET_EDGE_CONFIRMED",
                expected_gross_return_bps=forecast.expected_return_bps,
                estimated_friction_bps=forecast.estimated_friction_bps,
                expected_net_edge_bps=net_edge,
                probability_positive=p_up,
                target_horizon_min=opt_h,
                confidence_score=conf,
                suggested_allocation_pct=alloc_pct,
                is_authorized=True,
            )

        return EntryDecision(
            symbol=prediction.symbol,
            timestamp=prediction.timestamp,
            action="SKIP",
            reason="INSUFFICIENT_NET_EDGE",
            expected_gross_return_bps=forecast.expected_return_bps,
            estimated_friction_bps=forecast.estimated_friction_bps,
            expected_net_edge_bps=net_edge,
            probability_positive=p_up,
            target_horizon_min=opt_h,
            confidence_score=conf,
            suggested_allocation_pct=0.0,
            is_authorized=False,
        )
