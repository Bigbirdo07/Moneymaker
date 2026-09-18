"""Domain types, enums, and data models for the platform."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MarketRegime(str, Enum):
    """Market regime classification."""
    BULL_LOW_VOL = "BULL_LOW_VOL"
    BULL_HIGH_VOL = "BULL_HIGH_VOL"
    BEAR_LOW_VOL = "BEAR_LOW_VOL"
    BEAR_HIGH_VOL = "BEAR_HIGH_VOL"
    SIDEWAYS = "SIDEWAYS"
    UNKNOWN = "UNKNOWN"


class SessionType(str, Enum):
    """Trading session type."""
    PREMARKET = "PREMARKET"
    REGULAR = "REGULAR"
    POSTMARKET = "POSTMARKET"
    CLOSED = "CLOSED"


class EvidenceClass(str, Enum):
    """Evidence tagging class for provenance integrity."""
    HISTORICAL_REPLAY = "HISTORICAL_REPLAY"
    SIMULATED_EXECUTION = "SIMULATED_EXECUTION"
    HINDSIGHT_ORACLE = "HINDSIGHT_ORACLE"
    MODEL_PREDICTION = "MODEL_PREDICTION"
    RESEARCH_FINDING = "RESEARCH_FINDING"
    REAL_HISTORICAL_MARKET_DATA = "REAL_HISTORICAL_MARKET_DATA"
    SIMULATED_EXECUTION_ON_REAL_MARKET_DATA = "SIMULATED_EXECUTION_ON_REAL_MARKET_DATA"


class SignalDirection(str, Enum):
    """Direction of a trading signal."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    NO_TRADE = "NO_TRADE"
    EXIT = "EXIT"


class OrderType(str, Enum):
    """Order type for execution."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderSide(str, Enum):
    """Order side."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    """Status of an order."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class RiskDecisionStatus(str, Enum):
    """Risk engine evaluation verdict."""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RESIZED = "RESIZED"


@dataclass(frozen=True)
class Bar:
    """Canonical market data bar observation."""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None
    trade_count: Optional[int] = None

    def __post_init__(self) -> None:
        if self.high < self.low:
            raise ValueError(f"High ({self.high}) cannot be less than low ({self.low}) for {self.symbol} at {self.timestamp}")
        if self.open < self.low or self.open > self.high:
            raise ValueError(f"Open ({self.open}) out of range [{self.low}, {self.high}] for {self.symbol} at {self.timestamp}")
        if self.close < self.low or self.close > self.high:
            raise ValueError(f"Close ({self.close}) out of range [{self.low}, {self.high}] for {self.symbol} at {self.timestamp}")
        if self.volume < 0:
            raise ValueError(f"Volume ({self.volume}) cannot be negative for {self.symbol} at {self.timestamp}")


@dataclass
class Signal:
    """Quantitative signal output from an alpha model or strategy."""
    symbol: str
    timestamp: datetime
    direction: SignalDirection
    signal_strength: float  # Normalized magnitude, e.g. [-1.0, 1.0] or [0.0, 1.0]
    expected_return: float  # Expected return over the holding period
    confidence: float       # Calibrated probability or confidence [0.0, 1.0]
    expected_holding_period: int  # In minutes or bars
    model_version: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradeProposal:
    """Trade proposal generated from signals or analyst modules."""
    symbol: str
    timestamp: datetime
    action: SignalDirection
    confidence: float
    suggested_position_pct: float
    suggested_stop_pct: float
    suggested_target_pct: float
    expected_holding_minutes: int
    thesis: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskDecision:
    """Deterministic risk evaluation verdict."""
    status: RiskDecisionStatus
    original_position_pct: float
    approved_position_pct: float
    reason: str
    approved_shares: int = 0
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None


@dataclass
class Order:
    """Execution order representation."""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    created_at: datetime
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    filled_avg_price: float = 0.0
    fee_paid: float = 0.0


@dataclass
class Fill:
    """Execution fill event."""
    fill_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    slippage_cost: float
    spread_cost: float
    fee: float
    timestamp: datetime


@dataclass
class Position:
    """Portfolio position state."""
    symbol: str
    shares: int
    avg_entry_price: float
    current_price: float
    entry_timestamp: datetime
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    max_holding_bars: Optional[int] = None
    bars_held: int = 0

    @property
    def market_value(self) -> float:
        return self.shares * self.current_price

    @property
    def cost_basis(self) -> float:
        return self.shares * self.avg_entry_price

    def update_price(self, price: float) -> None:
        self.current_price = price
        self.unrealized_pnl = (self.current_price - self.avg_entry_price) * self.shares


@dataclass
class PortfolioState:
    """Ledger state of the portfolio at a single point in time."""
    timestamp: datetime
    cash: float
    buying_power: float
    positions: Dict[str, Position] = field(default_factory=dict)
    portfolio_value: float = 1000.0
    initial_capital: float = 1000.0
    daily_pnl: float = 0.0
    total_realized_pnl: float = 0.0
    total_fees: float = 0.0
    total_slippage: float = 0.0
    peak_portfolio_value: float = 1000.0
    drawdown_pct: float = 0.0
    max_drawdown_pct: float = 0.0

    def update_metrics(self) -> None:
        positions_market_value = sum(p.market_value for p in self.positions.values())
        self.portfolio_value = self.cash + positions_market_value
        self.buying_power = max(0.0, self.cash)
        if self.portfolio_value > self.peak_portfolio_value:
            self.peak_portfolio_value = self.portfolio_value
        if self.peak_portfolio_value > 0:
            self.drawdown_pct = (self.peak_portfolio_value - self.portfolio_value) / self.peak_portfolio_value
        else:
            self.drawdown_pct = 0.0
        if self.drawdown_pct > self.max_drawdown_pct:
            self.max_drawdown_pct = self.drawdown_pct
