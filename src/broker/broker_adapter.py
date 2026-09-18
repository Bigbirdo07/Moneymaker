"""
Abstract Broker Adapter Interface (Phase F).

Defines the contract for paper execution adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from src.broker.order_intent import OrderIntent, BrokerOrder, BrokerFill
from src.broker.execution_environment import ExecutionEnvironment, validate_execution_environment


@dataclass
class AccountSnapshot:
    account_id: str
    is_paper: bool
    currency: str
    equity: float
    cash: float
    buying_power: float
    status: str


class BrokerAdapter(ABC):
    """
    Abstract interface for broker interaction in PAPER / SIMULATION modes.
    """
    def __init__(self, environment: ExecutionEnvironment):
        validate_execution_environment(environment)
        self.environment = environment

    @abstractmethod
    def get_account(self) -> AccountSnapshot:
        """Retrieves verified account snapshot."""
        pass

    @abstractmethod
    def get_positions(self) -> Dict[str, float]:
        """Returns symbol -> current shares map."""
        pass

    @abstractmethod
    def get_open_orders(self) -> List[BrokerOrder]:
        """Returns list of currently active open broker orders."""
        pass

    @abstractmethod
    def submit_order(self, intent: OrderIntent) -> BrokerOrder:
        """Idempotently submits an order intent to the broker."""
        pass

    @abstractmethod
    def cancel_order(self, broker_order_id: str) -> bool:
        """Cancels an existing open order."""
        pass

    @abstractmethod
    def close_position(self, symbol: str) -> Optional[BrokerOrder]:
        """Liquidates any open position in the given symbol."""
        pass

    @abstractmethod
    def close_all_positions(self) -> List[BrokerOrder]:
        """Liquidates all open positions for EOD flattening."""
        pass

    @abstractmethod
    def get_recent_fills(self, limit: int = 50) -> List[BrokerFill]:
        """Returns recent execution fill records."""
        pass
