"""
Canonical Morning Intelligence Data Model (Phase E).

Defines structured dataclasses and enums for the premarket intelligence state,
market breadth, sector rankings, candidate watchlists, and morning briefs.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone


class MarketRegime(str, Enum):
    BULLISH_CONTINUATION = "BULLISH_CONTINUATION"
    BEARISH_CONTINUATION = "BEARISH_CONTINUATION"
    MEAN_REVERSION = "MEAN_REVERSION"
    LOW_VOL_CHOP = "LOW_VOL_CHOP"
    HIGH_VOL_SHOCK = "HIGH_VOL_SHOCK"
    REGIME_UNCERTAIN = "REGIME_UNCERTAIN"


class SessionGateState(str, Enum):
    GO = "GO"
    CAUTION = "CAUTION"
    NO_GO = "NO_GO"


class DispersionState(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class CandidateState(str, Enum):
    WATCH = "WATCH"
    NEAR_QUALIFIED = "NEAR_QUALIFIED"
    QUALIFIED = "QUALIFIED"
    EVENT_VETOED = "EVENT_VETOED"
    LIQUIDITY_REJECTED = "LIQUIDITY_REJECTED"
    DATA_REJECTED = "DATA_REJECTED"


@dataclass(frozen=True)
class MarketBreadthSnapshot:
    pct_above_vwap: float
    pct_positive_premarket: float
    cross_sectional_dispersion_bps: float
    dispersion_state: DispersionState
    advancers_count: int
    decliners_count: int
    total_evaluated: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pct_above_vwap": round(self.pct_above_vwap, 2),
            "pct_positive_premarket": round(self.pct_positive_premarket, 2),
            "cross_sectional_dispersion_bps": round(self.cross_sectional_dispersion_bps, 2),
            "dispersion_state": self.dispersion_state.value,
            "advancers_count": self.advancers_count,
            "decliners_count": self.decliners_count,
            "total_evaluated": self.total_evaluated,
        }


@dataclass(frozen=True)
class SectorPerformance:
    sector: str
    premarket_return_pct: float
    relative_return_vs_spy_bps: float
    breadth_pct_positive: float
    relative_volume: float
    eligible_symbol_count: int
    scanner_survivor_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sector": self.sector,
            "premarket_return_pct": round(self.premarket_return_pct, 2),
            "relative_return_vs_spy_bps": round(self.relative_return_vs_spy_bps, 1),
            "breadth_pct_positive": round(self.breadth_pct_positive, 1),
            "relative_volume": round(self.relative_volume, 2),
            "eligible_symbol_count": self.eligible_symbol_count,
            "scanner_survivor_count": self.scanner_survivor_count,
        }


@dataclass(frozen=True)
class MorningCandidate:
    symbol: str
    scanner_rank: int
    cross_sectional_rank: int
    sector: str
    premarket_return_pct: float
    relative_volume: float
    market_relative_return_bps: float
    sector_relative_return_bps: float
    estimated_execution_cost_bps: float
    candidate_state: CandidateState
    event_risk_status: str
    predicted_net_edge_bps: float = 0.0
    model_confidence: float = 0.0
    reason_codes: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "scanner_rank": self.scanner_rank,
            "cross_sectional_rank": self.cross_sectional_rank,
            "sector": self.sector,
            "premarket_return_pct": round(self.premarket_return_pct, 2),
            "relative_volume": round(self.relative_volume, 2),
            "market_relative_return_bps": round(self.market_relative_return_bps, 1),
            "sector_relative_return_bps": round(self.sector_relative_return_bps, 1),
            "estimated_execution_cost_bps": round(self.estimated_execution_cost_bps, 1),
            "candidate_state": self.candidate_state.value,
            "event_risk_status": self.event_risk_status,
            "predicted_net_edge_bps": round(self.predicted_net_edge_bps, 1),
            "model_confidence": round(self.model_confidence, 2),
            "reason_codes": self.reason_codes,
            "risk_factors": self.risk_factors,
        }


@dataclass(frozen=True)
class MorningRiskSummary:
    market_risk_level: str
    volatility_risk_level: str
    macro_risk_level: str
    event_risk_level: str
    liquidity_risk_level: str
    portfolio_risk_level: str
    system_risk_level: str
    overall_risk_state: str
    primary_risks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "market_risk_level": self.market_risk_level,
            "volatility_risk_level": self.volatility_risk_level,
            "macro_risk_level": self.macro_risk_level,
            "event_risk_level": self.event_risk_level,
            "liquidity_risk_level": self.liquidity_risk_level,
            "portfolio_risk_level": self.portfolio_risk_level,
            "system_risk_level": self.system_risk_level,
            "overall_risk_state": self.overall_risk_state,
            "primary_risks": self.primary_risks,
        }


@dataclass(frozen=True)
class MorningMarketState:
    date_str: str
    timestamp: str
    portfolio_equity: float
    capital_tier: str
    portfolio_risk_state: str
    market_regime: MarketRegime
    session_gate: SessionGateState
    spy_premarket_return_pct: float
    spy_overnight_return_pct: float
    breadth: MarketBreadthSnapshot
    strongest_sectors: List[SectorPerformance]
    weakest_sectors: List[SectorPerformance]
    raw_universe_count: int
    eligible_universe_count: int
    liquid_universe_count: int
    quality_pass_count: int
    event_veto_count: int
    fast_scanner_count: int
    deep_rank_count: int
    entry_qualified_count: int
    macro_events_today: List[Dict[str, Any]]
    top_candidates: List[MorningCandidate]
    risk_summary: MorningRiskSummary
    provenance_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date_str": self.date_str,
            "timestamp": self.timestamp,
            "portfolio_equity": round(self.portfolio_equity, 2),
            "capital_tier": self.capital_tier,
            "portfolio_risk_state": self.portfolio_risk_state,
            "market_regime": self.market_regime.value,
            "session_gate": self.session_gate.value,
            "spy_premarket_return_pct": round(self.spy_premarket_return_pct, 2),
            "spy_overnight_return_pct": round(self.spy_overnight_return_pct, 2),
            "breadth": self.breadth.to_dict(),
            "strongest_sectors": [s.to_dict() for s in self.strongest_sectors],
            "weakest_sectors": [s.to_dict() for s in self.weakest_sectors],
            "raw_universe_count": self.raw_universe_count,
            "eligible_universe_count": self.eligible_universe_count,
            "liquid_universe_count": self.liquid_universe_count,
            "quality_pass_count": self.quality_pass_count,
            "event_veto_count": self.event_veto_count,
            "fast_scanner_count": self.fast_scanner_count,
            "deep_rank_count": self.deep_rank_count,
            "entry_qualified_count": self.entry_qualified_count,
            "macro_events_today": self.macro_events_today,
            "top_candidates": [c.to_dict() for c in self.top_candidates],
            "risk_summary": self.risk_summary.to_dict(),
            "provenance_hash": self.provenance_hash,
        }
