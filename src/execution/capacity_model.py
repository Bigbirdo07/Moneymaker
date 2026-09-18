"""
Scalable Capacity & Market Impact Model (Phase B / Phase D).
Estimates ADV participation, minute volume participation, fill probability,
and safe position limits for capital scaling from $1,000 to $100,000+.
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, Optional
import numpy as np


class CapacityState(str, Enum):
    UNCONSTRAINED = "UNCONSTRAINED"
    LIQUIDITY_LIMITED = "LIQUIDITY_LIMITED"
    IMPACT_LIMITED = "IMPACT_LIMITED"
    NO_CAPACITY = "NO_CAPACITY"


@dataclass
class CapacityAssessment:
    """Capacity and market impact metrics for a target order size."""
    symbol: str
    target_dollars: float
    adv_dollars_30d: float
    minute_dollar_volume: float
    adv_participation_pct: float
    minute_participation_pct: float
    estimated_impact_bps: float
    max_safe_position_dollars: float
    is_capacity_approved: bool
    capacity_state: CapacityState = CapacityState.UNCONSTRAINED
    fill_probability: float = 1.0
    restriction_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "target_dollars": round(self.target_dollars, 2),
            "adv_dollars_30d": round(self.adv_dollars_30d, 2),
            "minute_dollar_volume": round(self.minute_dollar_volume, 2),
            "adv_participation_pct": round(self.adv_participation_pct, 4),
            "minute_participation_pct": round(self.minute_participation_pct, 4),
            "estimated_impact_bps": round(self.estimated_impact_bps, 2),
            "max_safe_position_dollars": round(self.max_safe_position_dollars, 2),
            "is_capacity_approved": self.is_capacity_approved,
            "capacity_state": self.capacity_state.value,
            "fill_probability": round(self.fill_probability, 3),
            "restriction_reason": self.restriction_reason,
        }


class CapacityModel:
    """
    Evaluates order capacity and market impact limits.
    """
    def __init__(
        self,
        max_adv_participation_pct: float = 0.010,       # Max 1.0% of 30d ADV
        max_minute_participation_pct: float = 0.050,    # Max 5.0% of expected 1-min volume
        max_acceptable_impact_bps: float = 10.0,
        impact_coefficient: float = 5.0,
    ) -> None:
        self.max_adv_participation_pct = max_adv_participation_pct
        self.max_minute_participation_pct = max_minute_participation_pct
        self.max_acceptable_impact_bps = max_acceptable_impact_bps
        self.impact_coefficient = impact_coefficient

    def estimate_capacity(
        self,
        symbol: str,
        target_dollars: float,
        adv_dollars_30d: float,
        minute_dollar_volume: Optional[float] = None,
    ) -> CapacityAssessment:
        """Formal Phase D API for capacity assessment."""
        return self.evaluate_capacity(symbol, target_dollars, adv_dollars_30d, minute_dollar_volume)

    def evaluate_capacity(
        self,
        symbol: str,
        target_dollars: float,
        adv_dollars_30d: float,
        minute_dollar_volume: Optional[float] = None,
    ) -> CapacityAssessment:
        """Evaluates whether an order size satisfies liquidity and impact constraints."""
        if adv_dollars_30d <= 0:
            return CapacityAssessment(
                symbol=symbol,
                target_dollars=target_dollars,
                adv_dollars_30d=0.0,
                minute_dollar_volume=0.0,
                adv_participation_pct=1.0,
                minute_participation_pct=1.0,
                estimated_impact_bps=999.0,
                max_safe_position_dollars=0.0,
                is_capacity_approved=False,
                capacity_state=CapacityState.NO_CAPACITY,
                fill_probability=0.0,
                restriction_reason="ZERO_OR_MISSING_ADV",
            )

        if minute_dollar_volume is None or minute_dollar_volume <= 0:
            minute_dollar_volume = max(10_000.0, adv_dollars_30d / 390.0)

        adv_part = target_dollars / max(1.0, adv_dollars_30d)
        min_part = target_dollars / max(1.0, minute_dollar_volume)

        # Almgren-Chriss non-linear square root impact model
        est_impact_bps = self.impact_coefficient * np.sqrt(max(0.00001, min_part))

        # Max safe position bounded by tighter of ADV and minute limits
        max_by_adv = adv_dollars_30d * self.max_adv_participation_pct
        max_by_min = minute_dollar_volume * self.max_minute_participation_pct
        max_safe_pos = float(min(max_by_adv, max_by_min))

        # Fill probability decay
        fill_prob = float(np.clip(1.0 - (min_part / (2.0 * self.max_minute_participation_pct)), 0.10, 1.0))

        if adv_part > self.max_adv_participation_pct or min_part > self.max_minute_participation_pct:
            cap_state = CapacityState.LIQUIDITY_LIMITED if adv_part > self.max_adv_participation_pct else CapacityState.IMPACT_LIMITED
            reason = f"ADV_PARTICIPATION_EXCEEDED: {adv_part:.2%}" if adv_part > self.max_adv_participation_pct else f"MINUTE_PARTICIPATION_EXCEEDED: {min_part:.2%}"
            return CapacityAssessment(
                symbol=symbol,
                target_dollars=target_dollars,
                adv_dollars_30d=adv_dollars_30d,
                minute_dollar_volume=minute_dollar_volume,
                adv_participation_pct=adv_part,
                minute_participation_pct=min_part,
                estimated_impact_bps=est_impact_bps,
                max_safe_position_dollars=max_safe_pos,
                is_capacity_approved=False,
                capacity_state=cap_state,
                fill_probability=fill_prob,
                restriction_reason=reason,
            )

        if est_impact_bps > self.max_acceptable_impact_bps:
            return CapacityAssessment(
                symbol=symbol,
                target_dollars=target_dollars,
                adv_dollars_30d=adv_dollars_30d,
                minute_dollar_volume=minute_dollar_volume,
                adv_participation_pct=adv_part,
                minute_participation_pct=min_part,
                estimated_impact_bps=est_impact_bps,
                max_safe_position_dollars=max_safe_pos,
                is_capacity_approved=False,
                capacity_state=CapacityState.IMPACT_LIMITED,
                fill_probability=fill_prob,
                restriction_reason=f"EXCESSIVE_MARKET_IMPACT: {est_impact_bps:.1f}bps > {self.max_acceptable_impact_bps:.1f}bps",
            )

        return CapacityAssessment(
            symbol=symbol,
            target_dollars=target_dollars,
            adv_dollars_30d=adv_dollars_30d,
            minute_dollar_volume=minute_dollar_volume,
            adv_participation_pct=adv_part,
            minute_participation_pct=min_part,
            estimated_impact_bps=est_impact_bps,
            max_safe_position_dollars=max_safe_pos,
            is_capacity_approved=True,
            capacity_state=CapacityState.UNCONSTRAINED,
            fill_probability=fill_prob,
            restriction_reason=None,
        )
