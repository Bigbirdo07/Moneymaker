"""
Capital Tiers & Multi-Tier Scaling Firewalls.

Defines operational capital limits, maximum allowed positions, exposure ceilings,
and participation thresholds across account scale tiers.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional


class CapitalTier(str, Enum):
    TIER_PAPER_1000 = "TIER_PAPER_1000"     # Initial $1,000 proving stage
    TIER_5000 = "TIER_5000"                 # $5,000 micro-scaling
    TIER_25000 = "TIER_25000"               # $25,000 PDT threshold tier
    TIER_100000 = "TIER_100000"             # $100,000 institutional validation tier


@dataclass(frozen=True)
class CapitalTierConstraints:
    tier_name: CapitalTier
    max_authorized_capital: float
    max_open_positions: int
    max_position_equity_pct: float
    max_sector_equity_pct: float
    max_adv_participation_pct: float
    max_minute_participation_pct: float
    min_trade_dollars: float


CAPITAL_TIER_CONFIGS: Dict[CapitalTier, CapitalTierConstraints] = {
    CapitalTier.TIER_PAPER_1000: CapitalTierConstraints(
        tier_name=CapitalTier.TIER_PAPER_1000,
        max_authorized_capital=1_500.0,
        max_open_positions=1,
        max_position_equity_pct=0.75,       # Allow up to 75% deployment into a single high-liquidity stock
        max_sector_equity_pct=0.75,
        max_adv_participation_pct=0.01,     # 1% ADV max
        max_minute_participation_pct=0.05,  # 5% minute volume max
        min_trade_dollars=100.0,            # Reject trivial trades < $100
    ),
    CapitalTier.TIER_5000: CapitalTierConstraints(
        tier_name=CapitalTier.TIER_5000,
        max_authorized_capital=7_500.0,
        max_open_positions=2,
        max_position_equity_pct=0.50,
        max_sector_equity_pct=0.60,
        max_adv_participation_pct=0.01,
        max_minute_participation_pct=0.05,
        min_trade_dollars=250.0,
    ),
    CapitalTier.TIER_25000: CapitalTierConstraints(
        tier_name=CapitalTier.TIER_25000,
        max_authorized_capital=35_000.0,
        max_open_positions=3,
        max_position_equity_pct=0.35,
        max_sector_equity_pct=0.50,
        max_adv_participation_pct=0.01,
        max_minute_participation_pct=0.05,
        min_trade_dollars=500.0,
    ),
    CapitalTier.TIER_100000: CapitalTierConstraints(
        tier_name=CapitalTier.TIER_100000,
        max_authorized_capital=150_000.0,
        max_open_positions=5,
        max_position_equity_pct=0.25,
        max_sector_equity_pct=0.40,
        max_adv_participation_pct=0.0075,   # 0.75% ADV max at scale
        max_minute_participation_pct=0.03,  # 3% minute volume max at scale
        min_trade_dollars=1_000.0,
    ),
}


def get_tier_for_equity(current_equity: float) -> CapitalTierConstraints:
    if current_equity <= 2_500.0:
        return CAPITAL_TIER_CONFIGS[CapitalTier.TIER_PAPER_1000]
    elif current_equity <= 10_000.0:
        return CAPITAL_TIER_CONFIGS[CapitalTier.TIER_5000]
    elif current_equity <= 50_000.0:
        return CAPITAL_TIER_CONFIGS[CapitalTier.TIER_25000]
    else:
        return CAPITAL_TIER_CONFIGS[CapitalTier.TIER_100000]
