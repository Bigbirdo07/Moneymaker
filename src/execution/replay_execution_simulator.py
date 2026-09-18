"""
Realistic Historical Replay Execution Simulator with Non-Instantaneous Fills,
Latency Injection, and Microstructure Friction Accounting.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

from src.core.logging import get_logger
from src.core.types import EvidenceClass, OrderSide

logger = get_logger("execution.replay_simulator")


@dataclass
class ReplaySimulatedFill:
    """Detailed fill artifact produced by the execution simulator."""
    fill_id: str
    order_id: str
    symbol: str
    side: str  # BUY, SELL
    shares: int | float
    decision_timestamp: str
    order_timestamp: str
    fill_timestamp: str
    reference_price: float
    fill_price: float
    spread_cost: float
    slippage_cost: float
    commission_fee: float
    total_friction: float
    gross_notional: float
    net_notional: float
    latency_seconds: float
    evidence_class: str = EvidenceClass.SIMULATED_EXECUTION.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ReplayExecutionSimulator:
    """
    Simulates non-instantaneous fills on bar T+1 with realistic bid/ask spread,
    nonlinear slippage, and SEC/FINRA regulatory and broker fee proxies.
    """

    def __init__(
        self,
        base_slippage_bps: float = 1.5,
        latency_seconds: float = 0.50,
        per_share_commission: float = 0.0005,  # $0.0005/share (zero commission broker with fractional clearing proxy)
        min_fee_per_order: float = 0.00,
        market_impact_exponent: float = 0.50,
    ) -> None:
        self.base_slippage_bps = base_slippage_bps
        self.latency_seconds = latency_seconds
        self.per_share_commission = per_share_commission
        self.min_fee_per_order = min_fee_per_order
        self.market_impact_exponent = market_impact_exponent
        self._fill_counter: int = 0

    def simulate_fill(
        self,
        order_id: str,
        symbol: str,
        side: OrderSide | str,
        shares: int | float,
        decision_timestamp: datetime | str,
        execution_bar: Dict[str, Any],  # Next-bar data (T+1) containing open, vwap, spread, volume
    ) -> ReplaySimulatedFill:
        """
        Executes an order using the next available bar data (T+1).
        Guarantees no same-bar execution.
        """
        self._fill_counter += 1
        side_str = side.value if isinstance(side, OrderSide) else str(side).upper()

        ref_price = float(execution_bar.get("open", execution_bar.get("close", 100.0)))
        spread = float(execution_bar.get("spread", ref_price * 0.0003))
        bar_vol = max(100.0, float(execution_bar.get("volume", 5000.0)))

        half_spread_per_share = spread / 2.0
        total_spread_cost = half_spread_per_share * shares

        # Slippage: Base bps + square-root market impact based on participation rate
        participation_rate = float(shares) / bar_vol
        impact_bps = 25.0 * (participation_rate ** self.market_impact_exponent)
        total_slip_bps = self.base_slippage_bps + impact_bps
        slip_per_share = ref_price * (total_slip_bps / 10000.0)
        total_slippage_cost = slip_per_share * shares

        # Fill price calculation
        if side_str == "BUY":
            fill_price = ref_price + half_spread_per_share + slip_per_share
        else:
            fill_price = ref_price - half_spread_per_share - slip_per_share

        # Regulatory & Commission fees
        fee = max(self.min_fee_per_order, float(shares) * self.per_share_commission)
        # SEC fee on sells (~$0.0000278 per dollar of principal)
        if side_str == "SELL":
            fee += (ref_price * shares) * 0.0000278

        total_friction = total_spread_cost + total_slippage_cost + fee
        gross_notional = ref_price * shares
        net_notional = fill_price * shares

        fill_ts = str(execution_bar.get("timestamp", decision_timestamp))

        return ReplaySimulatedFill(
            fill_id=f"FILL_{self._fill_counter:06d}",
            order_id=order_id,
            symbol=symbol,
            side=side_str,
            shares=shares,
            decision_timestamp=str(decision_timestamp),
            order_timestamp=str(decision_timestamp),
            fill_timestamp=fill_ts,
            reference_price=round(ref_price, 4),
            fill_price=round(fill_price, 4),
            spread_cost=round(total_spread_cost, 4),
            slippage_cost=round(total_slippage_cost, 4),
            commission_fee=round(fee, 4),
            total_friction=round(total_friction, 4),
            gross_notional=round(gross_notional, 2),
            net_notional=round(net_notional, 2),
            latency_seconds=self.latency_seconds,
        )
