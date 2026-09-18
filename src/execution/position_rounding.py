"""
Position Rounding & Share Calculation.

Handles whole-share and fractional-share execution rounding, accounting for
price thresholds, minimum order increments, and residual dollar tracking.
"""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ShareRoundingResult:
    target_dollars: float
    share_price: float
    unrounded_shares: float
    rounded_shares: float
    actual_notional_dollars: float
    rounding_error_dollars: float
    allow_fractional: bool


class PositionRoundingEngine:
    """
    Computes exact order share quantities according to broker capabilities.
    """
    def __init__(self, allow_fractional: bool = False, fractional_precision: int = 4):
        self.allow_fractional = allow_fractional
        self.fractional_precision = fractional_precision

    def round_position(self, target_dollars: float, share_price: float) -> ShareRoundingResult:
        if share_price <= 0.0 or target_dollars <= 0.0:
            return ShareRoundingResult(
                target_dollars=target_dollars,
                share_price=share_price,
                unrounded_shares=0.0,
                rounded_shares=0.0,
                actual_notional_dollars=0.0,
                rounding_error_dollars=0.0,
                allow_fractional=self.allow_fractional,
            )

        unrounded = target_dollars / share_price

        if self.allow_fractional:
            # Round down to precision
            factor = 10 ** self.fractional_precision
            rounded = math.floor(unrounded * factor) / factor
        else:
            # Whole-share floor
            rounded = float(math.floor(unrounded))

        actual_notional = rounded * share_price
        rounding_error = target_dollars - actual_notional

        return ShareRoundingResult(
            target_dollars=target_dollars,
            share_price=share_price,
            unrounded_shares=unrounded,
            rounded_shares=rounded,
            actual_notional_dollars=actual_notional,
            rounding_error_dollars=rounding_error,
            allow_fractional=self.allow_fractional,
        )
