"""
Order Intent, Decision Separation & Idempotency Architecture (Phase F).

Enforces clean separation between:
1. TradeDecision: Quantitative model output (symbol, side, edge, confidence)
2. OrderIntent: Strategy-level authorized intent with unique idempotency ID
3. BrokerOrder: Actual provider payload transmitted to paper broker
4. BrokerFill: Execution fill confirmation from broker
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
from typing import Dict, List, Optional, Any


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True)
class TradeDecision:
    symbol: str
    side: OrderSide
    predicted_net_edge_bps: float
    model_confidence: float
    reason_codes: List[str]
    decision_timestamp: str


@dataclass(frozen=True)
class OrderIntent:
    order_intent_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    target_notional: float
    limit_price: Optional[float]
    stop_loss_price: Optional[float]
    time_in_force: str
    creation_timestamp: str
    client_order_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        session_id: str,
        symbol: str,
        side: OrderSide,
        quantity: int,
        target_notional: float,
        limit_price: Optional[float] = None,
        stop_loss_price: Optional[float] = None,
        order_type: OrderType = OrderType.MARKET,
        time_in_force: str = "day",
        timestamp: Optional[str] = None,
    ) -> "OrderIntent":
        t_str = timestamp or datetime.now(timezone.utc).isoformat()
        raw_hash = f"{session_id}_{symbol}_{side.value}_{quantity}_{t_str}"
        intent_id = f"INTENT_{hashlib.sha256(raw_hash.encode()).hexdigest()[:16]}"
        client_id = f"MM_{intent_id}"

        return cls(
            order_intent_id=intent_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            target_notional=target_notional,
            limit_price=limit_price,
            stop_loss_price=stop_loss_price,
            time_in_force=time_in_force,
            creation_timestamp=t_str,
            client_order_id=client_id,
        )


@dataclass
class BrokerOrder:
    broker_order_id: str
    client_order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    filled_quantity: int
    status: OrderStatus
    submitted_timestamp: str
    limit_price: Optional[float] = None
    avg_fill_price: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "broker_order_id": self.broker_order_id,
            "client_order_id": self.client_order_id,
            "symbol": self.symbol,
            "side": self.side.value if hasattr(self.side, "value") else str(self.side),
            "order_type": self.order_type.value if hasattr(self.order_type, "value") else str(self.order_type),
            "quantity": self.quantity,
            "filled_quantity": self.filled_quantity,
            "status": self.status.value if hasattr(self.status, "value") else str(self.status),
            "submitted_timestamp": self.submitted_timestamp,
            "limit_price": self.limit_price,
            "avg_fill_price": self.avg_fill_price,
        }


@dataclass(frozen=True)
class BrokerFill:
    fill_id: str
    broker_order_id: str
    client_order_id: str
    symbol: str
    side: OrderSide
    filled_shares: int
    fill_price: float
    fill_timestamp: str
    commission: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fill_id": self.fill_id,
            "broker_order_id": self.broker_order_id,
            "client_order_id": self.client_order_id,
            "symbol": self.symbol,
            "side": self.side.value if hasattr(self.side, "value") else str(self.side),
            "filled_shares": self.filled_shares,
            "fill_price": self.fill_price,
            "fill_timestamp": self.fill_timestamp,
            "commission": self.commission,
        }
