"""
Strategy Capital Ledger & Paper Capital Firewall (Phase F).

Enforces strict separation between broker-reported account balance and
Moneymaker's authorized strategy capital ($1,000 initial proving tier).
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from src.risk.capital_tiers import CapitalTier, CapitalTierConstraints, CAPITAL_TIER_CONFIGS


@dataclass
class StrategyCapitalLedger:
    """
    Authoritative ledger defining strategy-authorized capital.
    Broker paper accounts often default to $100,000; this ledger restricts
    all position sizing, risk budgets, and exposure ceilings to $1,000.
    """
    authorized_strategy_capital: float = 1000.0
    capital_tier: CapitalTier = CapitalTier.TIER_PAPER_1000
    allocated_exposure_dollars: float = 0.0
    current_cash_dollars: float = 1000.0
    realized_pnl_dollars: float = 0.0
    unrealized_pnl_dollars: float = 0.0

    @property
    def current_strategy_equity(self) -> float:
        return self.authorized_strategy_capital + self.realized_pnl_dollars + self.unrealized_pnl_dollars

    @property
    def max_position_dollars(self) -> float:
        tier_cfg = CAPITAL_TIER_CONFIGS[self.capital_tier]
        return self.current_strategy_equity * tier_cfg.max_position_equity_pct

    @property
    def max_risk_per_trade_dollars(self) -> float:
        # 0.75% max risk per trade
        return self.current_strategy_equity * 0.0075

    @property
    def max_open_positions(self) -> int:
        tier_cfg = CAPITAL_TIER_CONFIGS[self.capital_tier]
        return tier_cfg.max_open_positions

    def update_pnl(self, realized_delta: float = 0.0, unrealized: float = 0.0) -> None:
        self.realized_pnl_dollars += realized_delta
        self.unrealized_pnl_dollars = unrealized
        self.current_cash_dollars += realized_delta
