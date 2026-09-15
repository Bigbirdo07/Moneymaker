"""
Broker Abstraction Layer & Safety Architecture for Phase 3B.
Enforces paper-only execution safety, order lifecycle state machine, idempotent submission,
and standardized broker interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import pandas as pd


class ExecutionMode(str, Enum):
    SHADOW = "SHADOW"
    BROKER_PAPER = "BROKER_PAPER"
    LIVE = "LIVE"


def verify_execution_mode(mode: ExecutionMode) -> None:
    """Fatal safety check: strictly prohibits LIVE execution mode."""
    if mode == ExecutionMode.LIVE:
        raise RuntimeError(
            "FATAL SAFETY VIOLATION: LIVE money execution is strictly prohibited in Phase 3B. "
            "Only SHADOW or BROKER_PAPER modes are permitted."
        )


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    RISK_APPROVED = "RISK_APPROVED"
    SUBMITTING = "SUBMITTING"
    SUBMITTED = "SUBMITTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCEL_PENDING = "CANCEL_PENDING"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    ERROR = "ERROR"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


# Valid Order State Machine Transition Matrix
VALID_TRANSITIONS: Dict[OrderStatus, Set[OrderStatus]] = {
    OrderStatus.CREATED: {OrderStatus.RISK_APPROVED, OrderStatus.REJECTED, OrderStatus.ERROR},
    OrderStatus.RISK_APPROVED: {OrderStatus.SUBMITTING, OrderStatus.REJECTED, OrderStatus.CANCELLED},
    OrderStatus.SUBMITTING: {OrderStatus.SUBMITTED, OrderStatus.REJECTED, OrderStatus.ERROR},
    OrderStatus.SUBMITTED: {OrderStatus.ACKNOWLEDGED, OrderStatus.REJECTED, OrderStatus.ERROR},
    OrderStatus.ACKNOWLEDGED: {OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED, OrderStatus.CANCEL_PENDING, OrderStatus.EXPIRED, OrderStatus.REJECTED},
    OrderStatus.PARTIALLY_FILLED: {OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED, OrderStatus.CANCEL_PENDING, OrderStatus.EXPIRED},
    OrderStatus.CANCEL_PENDING: {OrderStatus.CANCELLED, OrderStatus.FILLED, OrderStatus.ERROR},
    OrderStatus.FILLED: set(),           # Terminal
    OrderStatus.CANCELLED: set(),        # Terminal
    OrderStatus.REJECTED: set(),         # Terminal
    OrderStatus.EXPIRED: set(),          # Terminal
    OrderStatus.ERROR: set(),            # Terminal
}


@dataclass
class OrderTimestamps:
    decision_created: pd.Timestamp
    risk_approved: Optional[pd.Timestamp] = None
    submit_started: Optional[pd.Timestamp] = None
    broker_received: Optional[pd.Timestamp] = None
    acknowledged: Optional[pd.Timestamp] = None
    first_fill: Optional[pd.Timestamp] = None
    final_fill: Optional[pd.Timestamp] = None
    cancel_requested: Optional[pd.Timestamp] = None
    cancel_confirmed: Optional[pd.Timestamp] = None


@dataclass
class BrokerOrder:
    client_order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    qty: float
    limit_price: Optional[float] = None
    broker_order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.CREATED
    filled_qty: float = 0.0
    avg_fill_price: float = 0.0
    timestamps: OrderTimestamps = field(default_factory=lambda: OrderTimestamps(decision_created=pd.Timestamp.now(tz=timezone.utc)))
    rejection_reason: Optional[str] = None
    signal_id: Optional[str] = None
    decision_id: Optional[str] = None

    def transition_to(self, new_status: OrderStatus, reason: Optional[str] = None) -> None:
        """Enforce strict order state machine transitions."""
        if new_status not in VALID_TRANSITIONS.get(self.status, set()):
            raise ValueError(
                f"Invalid Order State Transition for order {self.client_order_id}: "
                f"Cannot transition from {self.status} to {new_status}."
            )
        self.status = new_status
        if reason:
            self.rejection_reason = reason


@dataclass
class BrokerPosition:
    symbol: str
    qty: float
    avg_entry_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float


@dataclass
class BrokerAccount:
    account_id: str
    is_paper: bool
    cash: float
    buying_power: float
    portfolio_value: float
    currency: str = "USD"


@dataclass
class BrokerFill:
    fill_id: str
    client_order_id: str
    broker_order_id: str
    symbol: str
    side: OrderSide
    fill_qty: float
    fill_price: float
    fill_ts: pd.Timestamp
    fee: float = 0.0


class BrokerAdapter(ABC):
    """Provider-neutral abstract broker gateway for paper execution."""

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def verify_paper_environment(self) -> bool:
        """Explicitly verify that the broker account is in PAPER mode."""
        pass

    @abstractmethod
    def get_account(self) -> BrokerAccount:
        pass

    @abstractmethod
    def get_buying_power(self) -> float:
        pass

    @abstractmethod
    def get_positions(self) -> Dict[str, BrokerPosition]:
        pass

    @abstractmethod
    def get_open_orders(self) -> List[BrokerOrder]:
        pass

    @abstractmethod
    def submit_order(self, order: BrokerOrder) -> BrokerOrder:
        pass

    @abstractmethod
    def cancel_order(self, client_order_id: str) -> bool:
        pass

    @abstractmethod
    def replace_order(self, client_order_id: str, new_qty: float, new_price: Optional[float] = None) -> Optional[BrokerOrder]:
        pass

    @abstractmethod
    def get_order(self, client_order_id: str) -> Optional[BrokerOrder]:
        pass

    @abstractmethod
    def get_fills(self) -> List[BrokerFill]:
        pass

    @abstractmethod
    def close_position(self, symbol: str) -> Optional[BrokerOrder]:
        pass

    @abstractmethod
    def close_all_positions(self) -> List[BrokerOrder]:
        pass


class MockBrokerPaperAdapter(BrokerAdapter):
    """
    High-fidelity in-memory Mock Broker implementing paper-only semantics,
    simulated latency, rate limiting, partial fills, cancellations, and chaos injection.
    """

    def __init__(
        self,
        account_id: str = "PAPER_ACC_1001",
        initial_cash: float = 1000.0,
        simulated_latency_ms: float = 15.0,
        is_paper_verified: bool = True,
    ):
        self.account_id = account_id
        self.cash = initial_cash
        self.is_paper_verified = is_paper_verified
        self.simulated_latency_ms = simulated_latency_ms
        self._connected = False

        self._orders: Dict[str, BrokerOrder] = {}  # client_order_id -> BrokerOrder
        self._broker_order_map: Dict[str, str] = {}  # broker_order_id -> client_order_id
        self._positions: Dict[str, BrokerPosition] = {}
        self._fills: List[BrokerFill] = []
        self._processed_idempotent_ids: Set[str] = set()

        # Failure / Chaos injection flags
        self.inject_network_timeout = False
        self.inject_rate_limit = False
        self.inject_order_rejection = False

    def connect(self) -> bool:
        if not self.is_paper_verified:
            raise RuntimeError("CRITICAL: Failed paper environment verification. Aborting startup.")
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def verify_paper_environment(self) -> bool:
        return self.is_paper_verified

    def get_account(self) -> BrokerAccount:
        pos_val = sum(p.market_value for p in self._positions.values())
        return BrokerAccount(
            account_id=self.account_id,
            is_paper=self.is_paper_verified,
            cash=self.cash,
            buying_power=self.cash,
            portfolio_value=self.cash + pos_val,
        )

    def get_buying_power(self) -> float:
        return self.cash

    def get_positions(self) -> Dict[str, BrokerPosition]:
        return dict(self._positions)

    def get_open_orders(self) -> List[BrokerOrder]:
        return [o for o in self._orders.values() if o.status in (OrderStatus.SUBMITTED, OrderStatus.ACKNOWLEDGED, OrderStatus.PARTIALLY_FILLED, OrderStatus.CANCEL_PENDING)]

    def get_order(self, client_order_id: str) -> Optional[BrokerOrder]:
        return self._orders.get(client_order_id)

    def get_fills(self) -> List[BrokerFill]:
        return list(self._fills)

    def submit_order(self, order: BrokerOrder) -> BrokerOrder:
        """Idempotent order submission with state transitions and error simulation."""
        if not self._connected:
            raise ConnectionError("Broker is disconnected.")

        if self.inject_rate_limit:
            raise RuntimeError("429 Too Many Requests: Broker rate limit exceeded.")

        if self.inject_network_timeout:
            raise TimeoutError("Broker connection timed out during submission.")

        # Idempotency check: if client_order_id already processed, return existing order
        if order.client_order_id in self._orders:
            return self._orders[order.client_order_id]

        now = pd.Timestamp.now(tz=timezone.utc)
        order.timestamps.submit_started = now
        order.transition_to(OrderStatus.SUBMITTING)

        if self.inject_order_rejection:
            order.transition_to(OrderStatus.REJECTED, reason="INJECTED_REJECTION")
            self._orders[order.client_order_id] = order
            return order

        broker_order_id = f"BRK_{order.client_order_id}"
        order.broker_order_id = broker_order_id
        order.timestamps.broker_received = now + pd.Timedelta(milliseconds=self.simulated_latency_ms)
        order.transition_to(OrderStatus.SUBMITTED)

        order.timestamps.acknowledged = now + pd.Timedelta(milliseconds=self.simulated_latency_ms * 2)
        order.transition_to(OrderStatus.ACKNOWLEDGED)

        self._orders[order.client_order_id] = order
        self._broker_order_map[broker_order_id] = order.client_order_id
        return order

    def execute_fill(
        self,
        client_order_id: str,
        fill_qty: float,
        fill_price: float,
        fill_ts: Optional[pd.Timestamp] = None,
        fee: float = 0.0,
    ) -> Optional[BrokerFill]:
        """Process a fill event (partial or full) against an acknowledged order."""
        if client_order_id not in self._orders:
            return None

        order = self._orders[client_order_id]
        if order.status not in (OrderStatus.ACKNOWLEDGED, OrderStatus.PARTIALLY_FILLED, OrderStatus.CANCEL_PENDING):
            return None

        now = fill_ts or pd.Timestamp.now(tz=timezone.utc)
        if order.timestamps.first_fill is None:
            order.timestamps.first_fill = now

        # Update order fill quantities
        new_filled_qty = order.filled_qty + fill_qty
        total_cost = (order.filled_qty * order.avg_fill_price) + (fill_qty * fill_price)
        order.avg_fill_price = total_cost / new_filled_qty if new_filled_qty > 0 else fill_price
        order.filled_qty = new_filled_qty

        # Create fill record
        fill_record = BrokerFill(
            fill_id=f"FILL_{client_order_id}_{len(self._fills)+1}",
            client_order_id=client_order_id,
            broker_order_id=order.broker_order_id or "",
            symbol=order.symbol,
            side=order.side,
            fill_qty=fill_qty,
            fill_price=fill_price,
            fill_ts=now,
            fee=fee,
        )
        self._fills.append(fill_record)

        # Update account cash & positions
        if order.side == OrderSide.BUY:
            outlay = (fill_qty * fill_price) + fee
            self.cash -= outlay
            if order.symbol in self._positions:
                pos = self._positions[order.symbol]
                new_qty = pos.qty + fill_qty
                pos.avg_entry_price = ((pos.qty * pos.avg_entry_price) + (fill_qty * fill_price)) / new_qty
                pos.qty = new_qty
                pos.current_price = fill_price
                pos.market_value = new_qty * fill_price
            else:
                self._positions[order.symbol] = BrokerPosition(
                    symbol=order.symbol,
                    qty=fill_qty,
                    avg_entry_price=fill_price,
                    current_price=fill_price,
                    market_value=fill_qty * fill_price,
                    unrealized_pnl=0.0,
                )
        elif order.side == OrderSide.SELL:
            proceeds = (fill_qty * fill_price) - fee
            self.cash += proceeds
            if order.symbol in self._positions:
                pos = self._positions[order.symbol]
                pos.qty -= fill_qty
                if pos.qty <= 1e-6:
                    self._positions.pop(order.symbol)
                else:
                    pos.current_price = fill_price
                    pos.market_value = pos.qty * fill_price

        # Update order status
        if order.filled_qty >= order.qty * 0.9999:
            order.timestamps.final_fill = now
            order.transition_to(OrderStatus.FILLED)
        else:
            order.transition_to(OrderStatus.PARTIALLY_FILLED)

        return fill_record

    def cancel_order(self, client_order_id: str) -> bool:
        if client_order_id not in self._orders:
            return False

        order = self._orders[client_order_id]
        if order.status not in (OrderStatus.ACKNOWLEDGED, OrderStatus.PARTIALLY_FILLED):
            return False

        now = pd.Timestamp.now(tz=timezone.utc)
        order.timestamps.cancel_requested = now
        order.transition_to(OrderStatus.CANCEL_PENDING)

        order.timestamps.cancel_confirmed = now + pd.Timedelta(milliseconds=self.simulated_latency_ms)
        order.transition_to(OrderStatus.CANCELLED)
        return True

    def replace_order(self, client_order_id: str, new_qty: float, new_price: Optional[float] = None) -> Optional[BrokerOrder]:
        if client_order_id not in self._orders:
            return None
        cancelled = self.cancel_order(client_order_id)
        if not cancelled:
            return None
        old_order = self._orders[client_order_id]
        new_order = BrokerOrder(
            client_order_id=f"{client_order_id}_R",
            symbol=old_order.symbol,
            side=old_order.side,
            order_type=old_order.order_type,
            qty=new_qty,
            limit_price=new_price or old_order.limit_price,
            signal_id=old_order.signal_id,
            decision_id=old_order.decision_id,
        )
        new_order.transition_to(OrderStatus.RISK_APPROVED)
        return self.submit_order(new_order)

    def close_position(self, symbol: str) -> Optional[BrokerOrder]:
        if symbol not in self._positions:
            return None
        pos = self._positions[symbol]
        sell_order = BrokerOrder(
            client_order_id=f"CLOSE_{symbol}_{int(datetime.now().timestamp())}",
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            qty=pos.qty,
        )
        sell_order.transition_to(OrderStatus.RISK_APPROVED)
        submitted = self.submit_order(sell_order)
        # Immediate market fill
        self.execute_fill(submitted.client_order_id, fill_qty=pos.qty, fill_price=pos.current_price)
        return submitted

    def close_all_positions(self) -> List[BrokerOrder]:
        closed = []
        for sym in list(self._positions.keys()):
            ord_res = self.close_position(sym)
            if ord_res:
                closed.append(ord_res)
        return closed
