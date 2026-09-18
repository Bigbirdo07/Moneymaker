"""
Morning Candidate Pipeline (Phase E).

Coordinates FastScanner filtering, V3 ranking, estimated execution costs,
and event risk status to produce the morning candidate watchlist.
"""

from typing import List, Dict, Any, Optional
import numpy as np

from src.intelligence.morning_market_state import MorningCandidate, CandidateState
from src.events.event_risk_policy import EventRiskPolicy
from src.execution.dynamic_cost_model import ExpectedExecutionCost


class MorningCandidatePipeline:
    """
    Builds structured morning candidate watchlists.
    """
    def __init__(
        self,
        cost_model: Optional[ExpectedExecutionCost] = None,
        event_policy: Optional[EventRiskPolicy] = None,
    ):
        self.cost_model = cost_model or ExpectedExecutionCost()
        self.event_policy = event_policy or EventRiskPolicy()

    def build_candidates(
        self,
        date_str: str,
        timestamp: str,
        scanner_symbols: List[str],
        symbol_returns_pct: Dict[str, float],
        symbol_rel_vol: Dict[str, float],
        symbol_sectors: Dict[str, str],
        spy_return_pct: float,
        predicted_edges_bps: Optional[Dict[str, float]] = None,
        confidences: Optional[Dict[str, float]] = None,
    ) -> List[MorningCandidate]:
        candidates: List[MorningCandidate] = []
        edges = predicted_edges_bps or {}
        confs = confidences or {}

        for idx, sym in enumerate(scanner_symbols):
            ret = symbol_returns_pct.get(sym, 0.0)
            rvol = symbol_rel_vol.get(sym, 1.0)
            sec = symbol_sectors.get(sym, "UNKNOWN")
            mkt_rel = (ret - spy_return_pct) * 100.0
            edge = edges.get(sym, 0.0)
            conf = confs.get(sym, 0.50)

            # Evaluate Event Risk
            event_dec = self.event_policy.evaluate(symbol=sym, timestamp=timestamp)
            cost_bps = 3.5  # Realistic 3.5 bps estimate

            reason_codes: List[str] = []
            risk_factors: List[str] = []

            if rvol >= 2.0:
                reason_codes.append("ELEVATED_PREMARKET_RELATIVE_VOLUME")
            if mkt_rel >= 50.0:
                reason_codes.append("TOP_TIER_MARKET_RELATIVE_MOMENTUM")

            if event_dec.is_vetoed:
                c_state = CandidateState.EVENT_VETOED
                risk_factors.extend(event_dec.reason_codes)
            elif edge >= 25.0 and conf >= 0.58:
                c_state = CandidateState.QUALIFIED
                reason_codes.append("EXCEEDS_ENTRY_NET_EDGE_HURDLE")
            elif edge >= 15.0:
                c_state = CandidateState.NEAR_QUALIFIED
                reason_codes.append("APPROACHING_ENTRY_HURDLE")
            else:
                c_state = CandidateState.WATCH

            candidates.append(MorningCandidate(
                symbol=sym,
                scanner_rank=idx + 1,
                cross_sectional_rank=idx + 1,
                sector=sec,
                premarket_return_pct=ret,
                relative_volume=rvol,
                market_relative_return_bps=mkt_rel,
                sector_relative_return_bps=mkt_rel * 0.8,
                estimated_execution_cost_bps=cost_bps,
                candidate_state=c_state,
                event_risk_status="VETOED" if event_dec.is_vetoed else "CLEAR",
                predicted_net_edge_bps=edge,
                model_confidence=conf,
                reason_codes=reason_codes,
                risk_factors=risk_factors,
            ))

        return candidates
