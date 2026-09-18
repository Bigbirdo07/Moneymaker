"""
Real-Market Entry Model V3 for Phase 11B / Engine V3.
Two-Stage Entry Gating: Market Regime Gate -> Cross-Sectional Leader -> High Edge Hurdle (>= 25 bps) -> 1 Trade/Day Max.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass
from src.models.real_market_ranking_forecaster_v3 import MultiHorizonPredictionV3

logger = get_logger("signals.real_entry_model_v3")


@dataclass
class EntryDecisionV3:
    """Decision output from Entry Model V3."""
    symbol: str
    timestamp: str
    action: str  # "ENTER_LONG", "PASS_CASH", "VETO_RISK"
    target_horizon_min: int
    expected_net_edge_bps: float
    calibrated_probability: float
    decision_reason: str
    evidence_class: str = EvidenceClass.SIMULATED_EXECUTION_ON_REAL_MARKET_DATA.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "action": self.action,
            "target_horizon_min": self.target_horizon_min,
            "expected_net_edge_bps": self.expected_net_edge_bps,
            "calibrated_probability": self.calibrated_probability,
            "decision_reason": self.decision_reason,
            "evidence_class": self.evidence_class,
        }


class RealMarketEntryModelV3:
    """
    Strict two-stage selective entry gate with cost-awareness and daily trade capping.
    """

    def __init__(
        self,
        min_net_edge_bps: float = 25.0,
        min_calibrated_prob: float = 0.58,
        max_daily_trades: int = 1,
        re_entry_cooldown_bars: int = 60,
    ) -> None:
        self.min_net_edge_bps = min_net_edge_bps
        self.min_calibrated_prob = min_calibrated_prob
        self.max_daily_trades = max_daily_trades
        self.re_entry_cooldown_bars = re_entry_cooldown_bars

    def evaluate_candidates(
        self,
        predictions: List[MultiHorizonPredictionV3],
        current_daily_trades: int,
        last_exit_bars_ago: Dict[str, int],
        has_active_position: bool,
    ) -> List[EntryDecisionV3]:
        """
        Ranks and gates candidates at timestamp T.
        """
        decisions = []

        # Enforce daily trade cap and single position limit
        if current_daily_trades >= self.max_daily_trades or has_active_position:
            for p in predictions:
                decisions.append(
                    EntryDecisionV3(
                        symbol=p.symbol,
                        timestamp=p.timestamp,
                        action="PASS_CASH",
                        target_horizon_min=p.optimal_target_horizon_min,
                        expected_net_edge_bps=p.best_expected_net_edge_bps,
                        calibrated_probability=p.best_calibrated_prob,
                        decision_reason="DAILY_TRADE_LIMIT_OR_ACTIVE_POSITION_REACHED",
                    )
                )
            return decisions

        # Filter tradable candidates
        eligible = []
        for p in predictions:
            # Stage 1: Market Regime Gate
            if not p.is_tradable_regime:
                decisions.append(
                    EntryDecisionV3(
                        symbol=p.symbol,
                        timestamp=p.timestamp,
                        action="VETO_RISK",
                        target_horizon_min=p.optimal_target_horizon_min,
                        expected_net_edge_bps=p.best_expected_net_edge_bps,
                        calibrated_probability=p.best_calibrated_prob,
                        decision_reason="STAGE_1_MARKET_REGIME_UNFAVORABLE",
                    )
                )
                continue

            # Cooldown check
            if last_exit_bars_ago.get(p.symbol, 999) < self.re_entry_cooldown_bars:
                decisions.append(
                    EntryDecisionV3(
                        symbol=p.symbol,
                        timestamp=p.timestamp,
                        action="PASS_CASH",
                        target_horizon_min=p.optimal_target_horizon_min,
                        expected_net_edge_bps=p.best_expected_net_edge_bps,
                        calibrated_probability=p.best_calibrated_prob,
                        decision_reason="COOLDOWN_ACTIVE",
                    )
                )
                continue

            # Stage 3: High Net Edge Hurdle
            if p.best_expected_net_edge_bps >= self.min_net_edge_bps and p.best_calibrated_prob >= self.min_calibrated_prob:
                eligible.append(p)
            else:
                decisions.append(
                    EntryDecisionV3(
                        symbol=p.symbol,
                        timestamp=p.timestamp,
                        action="PASS_CASH",
                        target_horizon_min=p.optimal_target_horizon_min,
                        expected_net_edge_bps=p.best_expected_net_edge_bps,
                        calibrated_probability=p.best_calibrated_prob,
                        decision_reason=f"BELOW_HURDLE_EDGE_{p.best_expected_net_edge_bps:.1f}bps_OR_PROB_{p.best_calibrated_prob:.2f}",
                    )
                )

        if not eligible:
            return decisions

        # Stage 2: Pick the single highest edge leader
        eligible.sort(key=lambda x: x.best_expected_net_edge_bps, reverse=True)
        winner = eligible[0]

        decisions.append(
            EntryDecisionV3(
                symbol=winner.symbol,
                timestamp=winner.timestamp,
                action="ENTER_LONG",
                target_horizon_min=winner.optimal_target_horizon_min,
                expected_net_edge_bps=winner.best_expected_net_edge_bps,
                calibrated_probability=winner.best_calibrated_prob,
                decision_reason=f"ENGINE_V3_AUTHORIZED_EDGE_{winner.best_expected_net_edge_bps:.1f}bps_PROB_{winner.best_calibrated_prob:.2f}",
            )
        )

        for other in eligible[1:]:
            decisions.append(
                EntryDecisionV3(
                    symbol=other.symbol,
                    timestamp=other.timestamp,
                    action="PASS_CASH",
                    target_horizon_min=other.optimal_target_horizon_min,
                    expected_net_edge_bps=other.best_expected_net_edge_bps,
                    calibrated_probability=other.best_calibrated_prob,
                    decision_reason="RANKED_BELOW_TOP_1_CANDIDATE",
                )
            )

        return decisions
