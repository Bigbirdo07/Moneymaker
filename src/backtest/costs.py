"""Transaction cost, bid-ask spread, and market friction modeling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from src.core.types import OrderSide


@dataclass
class CostBreakdown:
    """Breakdown of all frictions applied to an execution fill."""
    gross_price: float
    net_price: float
    half_spread_bps: float
    spread_cost: float
    slippage_bps: float
    slippage_cost: float
    commission: float
    total_friction: float


class TransactionCostModel:
    """
    Computes realistic execution friction including spread, market impact/slippage, and commissions.
    """

    def __init__(
        self,
        half_spread_bps: float = 1.5,
        base_slippage_bps: float = 2.0,
        commission_per_share: float = 0.0,
        commission_per_trade: float = 0.0,
    ) -> None:
        self.half_spread_bps = half_spread_bps
        self.base_slippage_bps = base_slippage_bps
        self.commission_per_share = commission_per_share
        self.commission_per_trade = commission_per_trade

    def calculate_fill(
        self,
        side: OrderSide,
        price: float,
        shares: int,
        observed_spread: Optional[float] = None,
        volume: Optional[float] = None,
    ) -> CostBreakdown:
        """
        Calculates execution fill price after deducting or adding frictions.
        
        For BUY: Net price = Gross Price * (1 + spread_bps/10000 + slippage_bps/10000)
        For SELL: Net price = Gross Price * (1 - spread_bps/10000 - slippage_bps/10000)
        """
        if shares <= 0 or price <= 0:
            return CostBreakdown(
                gross_price=price,
                net_price=price,
                half_spread_bps=0.0,
                spread_cost=0.0,
                slippage_bps=0.0,
                slippage_cost=0.0,
                commission=0.0,
                total_friction=0.0,
            )

        # Spread estimation: use observed spread if provided, else fallback to bps
        if observed_spread is not None and observed_spread > 0:
            half_spread_val = observed_spread / 2.0
            eff_half_spread_bps = (half_spread_val / price) * 10000.0
        else:
            eff_half_spread_bps = self.half_spread_bps
            half_spread_val = price * (eff_half_spread_bps / 10000.0)

        # Dynamic slippage based on volume participation (if volume provided)
        slippage_bps = self.base_slippage_bps
        if volume is not None and volume > 0:
            participation_rate = shares / volume
            if participation_rate > 0.01:
                # Add penalty for large order participation
                slippage_bps += min(20.0, (participation_rate - 0.01) * 200.0)

        slippage_val = price * (slippage_bps / 10000.0)

        # Total friction per share
        per_share_friction = half_spread_val + slippage_val

        if side == OrderSide.BUY:
            net_price = price + per_share_friction
        else:
            net_price = max(0.01, price - per_share_friction)

        spread_total_cost = half_spread_val * shares
        slippage_total_cost = slippage_val * shares
        commission_total = self.commission_per_trade + (self.commission_per_share * shares)
        total_friction = spread_total_cost + slippage_total_cost + commission_total

        return CostBreakdown(
            gross_price=round(price, 4),
            net_price=round(net_price, 4),
            half_spread_bps=round(eff_half_spread_bps, 2),
            spread_cost=round(spread_total_cost, 4),
            slippage_bps=round(slippage_bps, 2),
            slippage_cost=round(slippage_total_cost, 4),
            commission=round(commission_total, 4),
            total_friction=round(total_friction, 4),
        )
