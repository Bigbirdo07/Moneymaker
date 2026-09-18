"""Phase E: Premarket Intelligence and Morning Portfolio Manager module."""

from src.intelligence.macro_events import MacroEvent, MacroEventPolicy, MacroEventProvider, MacroImportance
from src.intelligence.market_breadth import MarketBreadthEngine
from src.intelligence.market_regime_engine import MarketRegimeEngine
from src.intelligence.morning_brief import MorningBriefService
from src.intelligence.morning_brief_renderer import DeterministicMorningBriefRenderer
from src.intelligence.morning_candidates import MorningCandidatePipeline
from src.intelligence.morning_market_state import (
    CandidateState,
    DispersionState,
    MarketBreadthSnapshot,
    MarketRegime,
    MorningCandidate,
    MorningMarketState,
    MorningRiskSummary,
    SectorPerformance,
    SessionGateState,
)
from src.intelligence.morning_narrative_validator import MorningNarrativeValidator, NarrativeValidationResult
from src.intelligence.sector_state import SectorStateEngine
from src.intelligence.session_gate import SessionGate, SessionGateDecision
from src.intelligence.system_readiness import ReadinessState, SystemReadinessMonitor, SystemReadinessReport

# Alias for backwards compatibility / semantic parity
MorningBrief = MorningMarketState
SystemReadiness = ReadinessState

__all__ = [
    "CandidateState",
    "DeterministicMorningBriefRenderer",
    "DispersionState",
    "MacroEvent",
    "MacroEventPolicy",
    "MacroEventProvider",
    "MacroImportance",
    "MarketBreadthEngine",
    "MarketBreadthSnapshot",
    "MarketRegime",
    "MarketRegimeEngine",
    "MorningBrief",
    "MorningBriefService",
    "MorningCandidate",
    "MorningCandidatePipeline",
    "MorningMarketState",
    "MorningNarrativeValidator",
    "MorningRiskSummary",
    "NarrativeValidationResult",
    "ReadinessState",
    "SectorPerformance",
    "SectorStateEngine",
    "SessionGate",
    "SessionGateDecision",
    "SessionGateState",
    "SystemReadiness",
    "SystemReadinessMonitor",
    "SystemReadinessReport",
]
