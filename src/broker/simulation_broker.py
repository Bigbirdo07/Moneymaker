"""
Simulation Broker Adapter (Phase F).

Provides high-fidelity, deterministic in-memory paper execution for unit tests,
chaos failure simulations, and offline verification without external network calls.
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone
import uuid

from src.broker.broker_adapter import BrokerAdapter, AccountSnapshot
from src.broker.execution_environment import ExecutionEnvironment
from src.broker.order_intent import (
    OrderIntent,
    BrokerOrder,
    BrokerFill,
    OrderStatus,
    OrderSide,
)


class SimulationBrokerAdapter(BrokerAdapter):
    """
    In-memory hermetic broker simulator.
    """
    def __init__(
        self,
        starting_cash: float = 100_000.0,
        slippage_bps: float = 2.0,
    ):
        super().__init__(environment=ExecutionEnvironment.SIMULATION)
        self.cash = starting_cash
        self.starting_cash = starting_cash
        self.positions: Dict[str, float] = {}
        self.orders: Dict[str, BrokerOrder] = {}
        self.fills: List[BrokerFill] = []
        self.slippage_bps = slippage_bps
        self.current_prices: Dict[str, float] = {}

    def set_price(self, symbol: str, price: float) -> None:
        self.current_prices[symbol] = price

    def get_account(self) -> AccountSnapshot:
        pos_val = sum(shares * self.current_prices.get(sym, 100.0) for sym, shares in self.positions.items())
        total_equity = self.cash + pos_val
        return AccountSnapshot(
            account_id="SIM_PAPER_ACCOUNT_001",
            is_paper=True,
            currency="USD",
            equity=total_equity,
            cash=self.cash,
            buying_power=total_equity * 2.0,
            status="ACTIVE",
        )

    def get_positions(self) -> Dict[str, float]:
        return {sym: shares for sym, shares in self.positions.items() if abs(shares) > 1e-5}

    def get_open_orders(self) -> List[BrokerOrder]:
        return [o for o in self.orders.values() if o.status in (OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED)]

    def submit_order(self, intent: OrderIntent) -> BrokerOrder:
        # Idempotency check: if client_order_id exists, return existing order
        for o in self.orders.values():
            if o.client_order_id == intent.client_order_id:
                return o

        b_id = f"SIM_ORD_{uuid.uuid4().hex[:12]}"
        order = BrokerOrder(
            broker_order_id=b_id,
            client_order_id=intent.client_order_id,
            symbol=intent.symbol,
            side=intent.side,
            order_type=intent.order_type,
            quantity=intent.quantity,
            filled_quantity=0,
            status=OrderStatus.SUBMITTED,
            submitted_timestamp=datetime.now(timezone.utc).isoformat(),
            limit_price=intent.limit_price,
        )
        self.orders[b_id] = order

        # Immediate simulation fill if price available
        mkt_price = self.current_prices.get(intent.symbol, intent.limit_price or 100.0)
        slip = mkt_price * (self.slippage_bps / 10000.0)
        fill_price = mkt_price + slip if intent.side == OrderSide.BUY else mkt_price - slip

        order.filled_quantity = intent.quantity
        order.avg_fill_price = fill_price
        order.status = OrderStatus.FILLED

        # Update position & cash
        if intent.side == OrderSide.BUY:
            cost = fill_price * intent.quantity
            self.cash -= cost
            self.positions[intent.symbol] = self.positions.get(intent.symbol, 0.0) + intent.quantity
        else:
            proceeds = fill_price * intent.quantity
            self.cash += proceeds
            self.positions[intent.symbol] = max(0.0, self.positions.get(intent.symbol, 0.0) - intent.quantity)

        fill = BrokerFill(
            fill_id=f"SIM_FILL_{uuid.uuid4().hex[:12]}",
            broker_order_id=b_id,
            client_order_id=intent.client_order_id,
            symbol=intent.symbol,
            side=intent.side,
            filled_shares=intent.quantity,
            fill_price=fill_price,
            fill_timestamp=datetime.now(timezone.utc).isoformat(),
            commission=0.0,
        )
        self.fills.append(fill)
        return order

    def cancel_order(self, broker_order_id: str) -> bool:
        if broker_order_id in self.orders:
            self.orders[broker_order_id].status = OrderStatus.CANCELED
            return True
        return False

    def close_position(self, symbol: str) -> Optional[BrokerOrder]:
        shares = int(self.positions.get(symbol, 0.0))
        if shares <= 0:
            return None
        intent = OrderIntent.create(
            session_id="SIM_CLOSE",
            symbol=symbol,
            side=OrderSide.SELL,
            quantity=shares,
            target_notional=shares * self.current_prices.get(symbol, 100.0),
        )
        return self.submit_order(intent)

    def close_all_positions(self) -> List[BrokerOrder]:
        closed = []
        for sym in list(self.positions.keys()):
            o = self.close_position(sym)
            if o:
                closed.append(o)
        return closed

    def get_recent_fills(self, limit: int = 50) -> List[BrokerFill]:
        return self.fills[-limit:]
