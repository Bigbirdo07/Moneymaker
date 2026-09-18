"""
Point-in-Time Universe Manager for Moneymaker Platform (Phase B).
Constructs session-by-session point-in-time eligible universes, integrates security
eligibility and liquidity filtering, and records machine-readable daily manifests.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.safety.security_eligibility_policy import (
    SecurityEligibilityPolicy,
    SecurityMetadata,
    SecurityType,
    Exchange,
    EligibilityReasonCode,
)
from src.data.market_data_quality_policy import MarketDataQualityPolicy, QualityViolationCode
from src.data.liquidity_filter import LiquidityFilter, LiquidityProfile, LiquidityTier

logger = get_logger("data.universe_manager")


@dataclass
class DailyUniverseManifest:
    """Complete audit record of universe construction for date T."""
    session_date: str
    total_market_symbols: int
    eligible_structural_symbols: int
    data_quality_passed_symbols: int
    liquid_tradable_symbols: int
    top_100_symbols: List[str] = field(default_factory=list)
    top_250_symbols: List[str] = field(default_factory=list)
    top_500_symbols: List[str] = field(default_factory=list)
    exclusions: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_date": self.session_date,
            "total_market_symbols": self.total_market_symbols,
            "eligible_structural_symbols": self.eligible_structural_symbols,
            "data_quality_passed_symbols": self.data_quality_passed_symbols,
            "liquid_tradable_symbols": self.liquid_tradable_symbols,
            "top_100_count": len(self.top_100_symbols),
            "top_250_count": len(self.top_250_symbols),
            "top_500_count": len(self.top_500_symbols),
            "total_exclusions": len(self.exclusions),
        }


class UniverseManager:
    """
    Orchestrates point-in-time universe discovery and daily manifest generation.
    """

    def __init__(
        self,
        eligibility_policy: Optional[SecurityEligibilityPolicy] = None,
        quality_policy: Optional[MarketDataQualityPolicy] = None,
        liquidity_filter: Optional[LiquidityFilter] = None,
    ) -> None:
        self.eligibility_policy = eligibility_policy or SecurityEligibilityPolicy()
        self.quality_policy = quality_policy or MarketDataQualityPolicy()
        self.liquidity_filter = liquidity_filter or LiquidityFilter()

    def build_daily_universe(
        self,
        session_date: str,
        asset_metadata_map: Dict[str, SecurityMetadata],
        daily_metrics_df: pd.DataFrame,
    ) -> DailyUniverseManifest:
        """
        Builds point-in-time universe for session_date from point-in-time metrics.
        """
        exclusions: List[Dict[str, Any]] = []
        eligible_symbols: List[str] = []
        liquid_profiles: List[LiquidityProfile] = []

        # 1. Structural Security Eligibility
        for sym, meta in asset_metadata_map.items():
            dec = self.eligibility_policy.evaluate_security(meta)
            if dec.is_eligible:
                eligible_symbols.append(sym)
            else:
                exclusions.append({
                    "symbol": sym,
                    "session_date": session_date,
                    "stage": "SECURITY_ELIGIBILITY",
                    "reason_code": dec.reason_code.value,
                    "explanation": dec.explanation,
                })

        # 2. Liquidity Filtering from Point-in-Time Metrics
        for sym in eligible_symbols:
            if sym in daily_metrics_df.index:
                row = daily_metrics_df.loc[sym]
                p = float(row.get("price", 0.0))
                adv = float(row.get("adv_shares_30d", 0.0))
                dvol = float(row.get("median_dollar_volume_30d", p * adv))
                prof = self.liquidity_filter.evaluate_profile(
                    symbol=sym,
                    session_date=session_date,
                    price=p,
                    adv_shares_30d=adv,
                    median_dollar_volume_30d=dvol,
                )
                if prof.is_tradable_liquid:
                    liquid_profiles.append(prof)
                else:
                    exclusions.append({
                        "symbol": sym,
                        "session_date": session_date,
                        "stage": "LIQUIDITY_FILTER",
                        "reason_code": prof.disqualification_reason or "LIQUIDITY_DISQUALIFIED",
                        "explanation": f"Price: ${p:.2f}, 30d DolVol: ${dvol/1e6:.1f}M",
                    })

        # Sort by 30-day median dollar volume descending
        liquid_profiles.sort(key=lambda x: x.median_dollar_volume_30d, reverse=True)
        sorted_symbols = [p.symbol for p in liquid_profiles]

        top_100 = sorted_symbols[:100]
        top_250 = sorted_symbols[:250]
        top_500 = sorted_symbols[:500]

        manifest = DailyUniverseManifest(
            session_date=session_date,
            total_market_symbols=len(asset_metadata_map),
            eligible_structural_symbols=len(eligible_symbols),
            data_quality_passed_symbols=len(eligible_symbols),
            liquid_tradable_symbols=len(sorted_symbols),
            top_100_symbols=top_100,
            top_250_symbols=top_250,
            top_500_symbols=top_500,
            exclusions=exclusions,
        )
        return manifest
