"""
Master Morning Brief Service (Phase E).

Coordinates premarket intelligence generation across regime, breadth,
sectors, macro events, candidate screening, risk budgeting, and session gates.
"""

from typing import Dict, List, Any, Optional
import hashlib
import json
from datetime import datetime, timezone

from src.intelligence.morning_market_state import (
    MorningMarketState,
    MarketRegime,
    SessionGateState,
    MarketBreadthSnapshot,
    SectorPerformance,
    MorningCandidate,
    MorningRiskSummary,
)
from src.intelligence.market_regime_engine import MarketRegimeEngine
from src.intelligence.session_gate import SessionGate
from src.intelligence.market_breadth import MarketBreadthEngine
from src.intelligence.sector_state import SectorStateEngine
from src.intelligence.macro_events import MacroEventProvider
from src.intelligence.morning_candidates import MorningCandidatePipeline
from src.intelligence.system_readiness import SystemReadinessMonitor
from src.risk.portfolio_risk_state import PortfolioRiskState
from src.risk.drawdown_state import AccountRiskState


class MorningBriefService:
    """
    Assembles the canonical MorningMarketState payload.
    """
    def __init__(
        self,
        regime_engine: Optional[MarketRegimeEngine] = None,
        session_gate: Optional[SessionGate] = None,
        breadth_engine: Optional[MarketBreadthEngine] = None,
        sector_engine: Optional[SectorStateEngine] = None,
        macro_provider: Optional[MacroEventProvider] = None,
        candidate_pipeline: Optional[MorningCandidatePipeline] = None,
        readiness_monitor: Optional[SystemReadinessMonitor] = None,
    ):
        self.regime_engine = regime_engine or MarketRegimeEngine()
        self.session_gate = session_gate or SessionGate()
        self.breadth_engine = breadth_engine or MarketBreadthEngine()
        self.sector_engine = sector_engine or SectorStateEngine()
        self.macro_provider = macro_provider or MacroEventProvider()
        self.candidate_pipeline = candidate_pipeline or MorningCandidatePipeline()
        self.readiness_monitor = readiness_monitor or SystemReadinessMonitor()

    def generate_morning_state(
        self,
        date_str: str,
        timestamp: str,
        portfolio_state: PortfolioRiskState,
        spy_premarket_return_pct: float,
        spy_overnight_return_pct: float,
        symbol_returns_pct: Dict[str, float],
        symbol_vwap_distances_pct: Dict[str, float],
        symbol_sectors: Dict[str, str],
        symbol_rel_vol: Dict[str, float],
        scanner_symbols: List[str],
        raw_universe_count: int = 4812,
        eligible_universe_count: int = 2945,
        liquid_universe_count: int = 826,
        quality_pass_count: int = 803,
        event_veto_count: int = 17,
    ) -> MorningMarketState:
        # 1. System Readiness Check
        readiness = self.readiness_monitor.evaluate_readiness(
            last_market_data_timestamp=timestamp,
            current_timestamp=timestamp,
        )

        # 2. Market Breadth Snapshot
        breadth = self.breadth_engine.compute_breadth(symbol_returns_pct, symbol_vwap_distances_pct)

        # 3. Market Regime Classification
        regime = self.regime_engine.classify_regime(
            spy_premarket_return_pct=spy_premarket_return_pct,
            spy_overnight_return_pct=spy_overnight_return_pct,
            breadth=breadth,
        )

        # 4. Sector Performance & Ranking
        sectors = self.sector_engine.evaluate_sectors(
            symbol_returns_pct=symbol_returns_pct,
            symbol_sectors=symbol_sectors,
            symbol_rel_vol=symbol_rel_vol,
            spy_return_pct=spy_premarket_return_pct,
            fast_scanner_symbols=scanner_symbols,
        )
        strongest = sectors[:3] if len(sectors) >= 3 else sectors
        weakest = sectors[-2:] if len(sectors) >= 2 else []

        # 5. Macro Events Check
        macro_events = self.macro_provider.get_events_for_date(date_str)
        is_macro_imminent = self.macro_provider.is_macro_release_imminent(timestamp)

        # 6. Session Gate Evaluation
        gate_dec = self.session_gate.evaluate(
            market_regime=regime,
            portfolio_risk_state=AccountRiskState.NORMAL,
            is_system_ready=readiness.is_ready_for_session,
            is_macro_event_imminent=is_macro_imminent,
        )

        # 7. Candidate Screening & Ranking
        candidates = self.candidate_pipeline.build_candidates(
            date_str=date_str,
            timestamp=timestamp,
            scanner_symbols=scanner_symbols,
            symbol_returns_pct=symbol_returns_pct,
            symbol_rel_vol=symbol_rel_vol,
            symbol_sectors=symbol_sectors,
            spy_return_pct=spy_premarket_return_pct,
        )
        entry_qualified = sum(1 for c in candidates if c.candidate_state == "QUALIFIED")

        # 8. Risk Summary
        risk_summary = MorningRiskSummary(
            market_risk_level="NORMAL" if gate_dec.gate_state == SessionGateState.GO else "ELEVATED",
            volatility_risk_level="NORMAL",
            macro_risk_level="ELEVATED" if is_macro_imminent else "LOW",
            event_risk_level="NORMAL",
            liquidity_risk_level="LOW",
            portfolio_risk_level="NOMINAL",
            system_risk_level="READY" if readiness.is_ready_for_session else "DEGRADED",
            overall_risk_state=gate_dec.gate_state.value,
            primary_risks=[f"Macro release window: {e.event_name}" for e in macro_events if e.importance == "HIGH"] or ["Standard market volatility"],
        )

        # Hash for provenance
        hash_payload = f"{date_str}_{timestamp}_{regime.value}_{gate_dec.gate_state.value}_{len(candidates)}"
        prov_hash = hashlib.sha256(hash_payload.encode()).hexdigest()[:16]

        return MorningMarketState(
            date_str=date_str,
            timestamp=timestamp,
            portfolio_equity=portfolio_state.current_equity,
            capital_tier="TIER_PAPER_1000",
            portfolio_risk_state="NORMAL",
            market_regime=regime,
            session_gate=gate_dec.gate_state,
            spy_premarket_return_pct=spy_premarket_return_pct,
            spy_overnight_return_pct=spy_overnight_return_pct,
            breadth=breadth,
            strongest_sectors=strongest,
            weakest_sectors=weakest,
            raw_universe_count=raw_universe_count,
            eligible_universe_count=eligible_universe_count,
            liquid_universe_count=liquid_universe_count,
            quality_pass_count=quality_pass_count,
            event_veto_count=event_veto_count,
            fast_scanner_count=len(scanner_symbols),
            deep_rank_count=min(12, len(scanner_symbols)),
            entry_qualified_count=entry_qualified,
            macro_events_today=[{"event_name": e.event_name, "scheduled": e.scheduled_timestamp, "importance": e.importance} for e in macro_events],
            top_candidates=candidates[:5],
            risk_summary=risk_summary,
            provenance_hash=prov_hash,
        )
