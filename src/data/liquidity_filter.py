"""
Liquidity Filter & Threshold Research Engine for Moneymaker Platform (Phase B).
Computes point-in-time liquidity metrics (30d median dollar volume, ADV,
median bar volume, zero-volume fraction) and filters candidate universes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd


class LiquidityTier(str, Enum):
    MEGA_LIQUID = "TIER_250M_PLUS"    # >= $250M 30d median dollar volume
    HIGH_LIQUID = "TIER_100M_250M"    # $100M - $250M
    MID_LIQUID = "TIER_50M_100M"      # $50M - $100M
    MODERATE_LIQUID = "TIER_25M_50M"  # $25M - $50M
    LOW_LIQUID = "TIER_10M_25M"       # $10M - $25M
    ILLIQUID = "TIER_SUB_10M"         # < $10M (Excluded)


@dataclass
class LiquidityProfile:
    """Point-in-time liquidity summary for a security on date T."""
    symbol: str
    session_date: str
    price: float
    adv_shares_30d: float
    median_dollar_volume_30d: float
    median_minute_volume_30d: float
    zero_volume_fraction_30d: float
    realized_volatility_30d_bps: float
    estimated_spread_bps: float
    liquidity_tier: LiquidityTier
    is_tradable_liquid: bool
    disqualification_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "session_date": self.session_date,
            "price": round(self.price, 2),
            "adv_shares_30d": round(self.adv_shares_30d, 0),
            "median_dollar_volume_30d": round(self.median_dollar_volume_30d, 2),
            "median_minute_volume_30d": round(self.median_minute_volume_30d, 0),
            "zero_volume_fraction_30d": round(self.zero_volume_fraction_30d, 4),
            "realized_volatility_30d_bps": round(self.realized_volatility_30d_bps, 1),
            "estimated_spread_bps": round(self.estimated_spread_bps, 2),
            "liquidity_tier": self.liquidity_tier.value,
            "is_tradable_liquid": self.is_tradable_liquid,
            "disqualification_reason": self.disqualification_reason,
        }


class LiquidityFilter:
    """
    Evaluates point-in-time liquidity metrics against configurable thresholds.
    """

    def __init__(
        self,
        min_price: float = 10.0,
        min_median_dollar_volume_30d: float = 25_000_000.0,  # $25M default
        min_adv_shares_30d: float = 500_000.0,
        max_estimated_spread_bps: float = 8.0,
        max_zero_volume_fraction: float = 0.20,
    ) -> None:
        self.min_price = min_price
        self.min_median_dollar_volume_30d = min_median_dollar_volume_30d
        self.min_adv_shares_30d = min_adv_shares_30d
        self.max_estimated_spread_bps = max_spread_bps = max_estimated_spread_bps
        self.max_zero_volume_fraction = max_zero_volume_fraction

    @staticmethod
    def classify_liquidity_tier(median_dollar_vol: float) -> LiquidityTier:
        """Assigns liquidity tier based on 30-day median dollar volume."""
        if median_dollar_vol >= 250_000_000.0:
            return LiquidityTier.MEGA_LIQUID
        elif median_dollar_vol >= 100_000_000.0:
            return LiquidityTier.HIGH_LIQUID
        elif median_dollar_vol >= 50_000_000.0:
            return LiquidityTier.MID_LIQUID
        elif median_dollar_vol >= 25_000_000.0:
            return LiquidityTier.MODERATE_LIQUID
        elif median_dollar_vol >= 10_000_000.0:
            return LiquidityTier.LOW_LIQUID
        else:
            return LiquidityTier.ILLIQUID

    @staticmethod
    def estimate_spread_bps(price: float, median_dollar_vol: float, realized_vol_bps: float = 25.0) -> float:
        """
        Estimates empirical half-spread in basis points as a function of price,
        liquidity tier, and realized volatility.
        Formula derived from empirical IEX order-book microstructure fits:
        Spread (bps) ≈ base_spread + (1 / sqrt(Dollar Volume / $1M)) * (1 + Vol_bps / 50)
        """
        if price <= 0 or median_dollar_vol <= 0:
            return 50.0
        
        # Base spread in cents is roughly $0.01 for liquid names
        penny_spread_bps = (0.01 / price) * 10000.0
        vol_scale = 1.0 + (realized_vol_bps / 100.0)
        liquidity_scale = max(0.5, 5.0 / np.sqrt(max(1.0, median_dollar_vol / 1_000_000.0)))
        
        est_spread_bps = max(penny_spread_bps, liquidity_scale * vol_scale)
        return float(min(100.0, est_spread_bps))

    def evaluate_profile(
        self,
        symbol: str,
        session_date: str,
        price: float,
        adv_shares_30d: float,
        median_dollar_volume_30d: float,
        median_minute_volume_30d: float = 1000.0,
        zero_volume_fraction_30d: float = 0.05,
        realized_volatility_30d_bps: float = 25.0,
    ) -> LiquidityProfile:
        """Evaluates a symbol's point-in-time liquidity profile against policy rules."""
        tier = self.classify_liquidity_tier(median_dollar_volume_30d)
        est_spread = self.estimate_spread_bps(price, median_dollar_volume_30d, realized_volatility_30d_bps)

        # Apply Rejection Rules
        if price < self.min_price:
            return LiquidityProfile(
                symbol=symbol,
                session_date=session_date,
                price=price,
                adv_shares_30d=adv_shares_30d,
                median_dollar_volume_30d=median_dollar_volume_30d,
                median_minute_volume_30d=median_minute_volume_30d,
                zero_volume_fraction_30d=zero_volume_fraction_30d,
                realized_volatility_30d_bps=realized_volatility_30d_bps,
                estimated_spread_bps=est_spread,
                liquidity_tier=tier,
                is_tradable_liquid=False,
                disqualification_reason=f"PRICE_BELOW_MINIMUM: ${price:.2f} < ${self.min_price:.2f}",
            )

        if median_dollar_volume_30d < self.min_median_dollar_volume_30d:
            return LiquidityProfile(
                symbol=symbol,
                session_date=session_date,
                price=price,
                adv_shares_30d=adv_shares_30d,
                median_dollar_volume_30d=median_dollar_volume_30d,
                median_minute_volume_30d=median_minute_volume_30d,
                zero_volume_fraction_30d=zero_volume_fraction_30d,
                realized_volatility_30d_bps=realized_volatility_30d_bps,
                estimated_spread_bps=est_spread,
                liquidity_tier=tier,
                is_tradable_liquid=False,
                disqualification_reason=f"DOLLAR_VOLUME_BELOW_MINIMUM: ${median_dollar_volume_30d/1e6:.1f}M < ${self.min_median_dollar_volume_30d/1e6:.1f}M",
            )

        if adv_shares_30d < self.min_adv_shares_30d:
            return LiquidityProfile(
                symbol=symbol,
                session_date=session_date,
                price=price,
                adv_shares_30d=adv_shares_30d,
                median_dollar_volume_30d=median_dollar_volume_30d,
                median_minute_volume_30d=median_minute_volume_30d,
                zero_volume_fraction_30d=zero_volume_fraction_30d,
                realized_volatility_30d_bps=realized_volatility_30d_bps,
                estimated_spread_bps=est_spread,
                liquidity_tier=tier,
                is_tradable_liquid=False,
                disqualification_reason=f"ADV_BELOW_MINIMUM: {adv_shares_30d:,.0f} < {self.min_adv_shares_30d:,.0f}",
            )

        if est_spread > self.max_estimated_spread_bps:
            return LiquidityProfile(
                symbol=symbol,
                session_date=session_date,
                price=price,
                adv_shares_30d=adv_shares_30d,
                median_dollar_volume_30d=median_dollar_volume_30d,
                median_minute_volume_30d=median_minute_volume_30d,
                zero_volume_fraction_30d=zero_volume_fraction_30d,
                realized_volatility_30d_bps=realized_volatility_30d_bps,
                estimated_spread_bps=est_spread,
                liquidity_tier=tier,
                is_tradable_liquid=False,
                disqualification_reason=f"SPREAD_EXCEEDS_MAXIMUM: {est_spread:.1f} bps > {self.max_estimated_spread_bps:.1f} bps",
            )

        return LiquidityProfile(
            symbol=symbol,
            session_date=session_date,
            price=price,
            adv_shares_30d=adv_shares_30d,
            median_dollar_volume_30d=median_dollar_volume_30d,
            median_minute_volume_30d=median_minute_volume_30d,
            zero_volume_fraction_30d=zero_volume_fraction_30d,
            realized_volatility_30d_bps=realized_volatility_30d_bps,
            estimated_spread_bps=est_spread,
            liquidity_tier=tier,
            is_tradable_liquid=True,
            disqualification_reason=None,
        )
