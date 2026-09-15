"""
Forward Signal, Decay, Calibration & Execution Quality Evaluation for Phase 3A.
Maintains the Rejected Opportunity Ledger and generates comparative forward metrics.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from src.execution.shadow_engine import ExecutionSimulationResult, LimitFillStatus


@dataclass
class RejectedOpportunityRecord:
    """Immutable record of any rejected candidate signal during shadow decision loop."""
    decision_id: str
    symbol: str
    timestamp: pd.Timestamp
    model_score: float
    meta_label_decision: str  # "TAKE_TRADE" or "REJECT_TRADE"
    rank: int
    spread_bps: float
    volatility_bps: float
    archetype: str
    regime: str
    rejection_reason: str  # e.g. "META_LABEL_REJECT", "COOLDOWN_ACTIVE", "RISK_REJECT", "LOW_RANK"
    future_realized_return_bps: Optional[float] = None


@dataclass
class ForwardDecayPoint:
    """Forward realized returns across multiple holding horizons for a single signal."""
    decision_id: str
    symbol: str
    timestamp: pd.Timestamp
    model_confidence: float
    ret_1m_bps: Optional[float]
    ret_2m_bps: Optional[float]
    ret_5m_bps: Optional[float]
    ret_10m_bps: Optional[float]
    ret_15m_bps: Optional[float]
    ret_20m_bps: Optional[float]
    ret_30m_bps: Optional[float]
    ret_45m_bps: Optional[float]
    ret_60m_bps: Optional[float]


class ForwardExecutionEvaluator:
    """Evaluates forward shadow execution, signal decay, and adverse selection."""

    def __init__(self):
        self.proposed_trades: List[ExecutionSimulationResult] = []
        self.rejected_records: List[RejectedOpportunityRecord] = []
        self.decay_records: List[ForwardDecayPoint] = []
        self.all_universe_scores: List[Dict] = []  # List of {timestamp, symbol, score, realized_15m_return}

    def record_execution(self, sim_result: ExecutionSimulationResult) -> None:
        self.proposed_trades.append(sim_result)

    def record_rejection(self, rejection: RejectedOpportunityRecord) -> None:
        self.rejected_records.append(rejection)

    def record_decay(self, decay_point: ForwardDecayPoint) -> None:
        self.decay_records.append(decay_point)

    def record_universe_score(self, timestamp: pd.Timestamp, symbol: str, score: float, realized_15m_return: float) -> None:
        self.all_universe_scores.append({
            "timestamp": timestamp,
            "symbol": symbol,
            "score": score,
            "realized_return": realized_15m_return,
        })

    def compute_forward_rank_ic(self) -> Tuple[float, float]:
        """Compute cross-sectional Spearman Rank IC across all eligible universe scores."""
        if len(self.all_universe_scores) < 10:
            return 0.0, 1.0

        scores = [item["score"] for item in self.all_universe_scores]
        realized = [item["realized_return"] for item in self.all_universe_scores]
        corr, pval = spearmanr(scores, realized)
        return float(corr), float(pval)

    def compute_adverse_selection_metrics(self) -> Dict[str, float]:
        """
        Compare post-fill forward returns against post-missed limit order returns.
        If filled trades systematically underperform missed trades, adverse selection is present.
        """
        limit_trades = [t for t in self.proposed_trades if t.limit_fill_status in (LimitFillStatus.FILLED, LimitFillStatus.ADVERSE_SELECTED, LimitFillStatus.MISSED)]
        if not limit_trades:
            return {"filled_count": 0, "missed_count": 0, "filled_avg_ret_bps": 0.0, "missed_avg_ret_bps": 0.0, "adverse_selection_bps": 0.0}

        filled = [t for t in limit_trades if t.limit_fill_status in (LimitFillStatus.FILLED, LimitFillStatus.ADVERSE_SELECTED) and t.future_15m_return_bps is not None]
        missed = [t for t in limit_trades if t.limit_fill_status == LimitFillStatus.MISSED and t.future_15m_return_bps is not None]

        filled_avg = float(np.mean([t.future_15m_return_bps for t in filled])) if filled else 0.0
        missed_avg = float(np.mean([t.future_15m_return_bps for t in missed])) if missed else 0.0

        # Adverse selection penalty is how much better missed trades were than filled trades
        adverse_gap = missed_avg - filled_avg

        return {
            "filled_count": len(filled),
            "missed_count": len(missed),
            "filled_avg_ret_bps": filled_avg,
            "missed_avg_ret_bps": missed_avg,
            "adverse_selection_bps": adverse_gap,
            "limit_fill_rate_pct": (len(filled) / len(limit_trades) * 100.0) if limit_trades else 0.0,
        }

    def compute_forward_decay_profile(self) -> Dict[str, float]:
        """Compute mean forward returns across horizons."""
        if not self.decay_records:
            return {}

        horizons = ["ret_1m_bps", "ret_2m_bps", "ret_5m_bps", "ret_10m_bps", "ret_15m_bps", "ret_20m_bps", "ret_30m_bps", "ret_45m_bps", "ret_60m_bps"]
        profile = {}
        for h in horizons:
            vals = [getattr(r, h) for r in self.decay_records if getattr(r, h) is not None]
            profile[h] = float(np.mean(vals)) if vals else 0.0

        return profile
