"""Cross-sectional opportunity ranker and cost-aware opportunity scoring engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr

from src.core.types import Signal, SignalDirection
from src.models.base import BaseMLModel


@dataclass
class RankedOpportunity:
    """Scored and ranked trading opportunity across universe securities."""
    timestamp: datetime
    symbol: str
    rank: int
    raw_score: float
    expected_return_bps: float
    estimated_friction_bps: float
    volatility_penalty_bps: float
    net_opportunity_score: float
    confidence: float
    is_selected: bool


@dataclass
class CrossSectionalEvaluation:
    """Statistical evaluation metrics for cross-sectional ranking."""
    mean_spearman_ic: float
    ic_t_stat: float
    ic_ir: float  # Information Ratio of IC
    top_decile_return_bps: float
    bottom_decile_return_bps: float
    long_short_spread_bps: float
    total_timestamps_evaluated: int


class OpportunityRanker:
    """
    Ranks multi-asset universe opportunities cross-sectionally at each timestamp
    using cost-aware risk-adjusted scoring.
    """

    def __init__(
        self,
        risk_penalty_lambda: float = 0.50, # Lambda weighting on volatility penalty
        base_friction_bps: float = 7.0,    # 1.5 bps spread * 2 + 2.0 bps slip * 2
        top_k: int = 3,                    # Select top k opportunities
        min_opportunity_score_bps: float = 2.0, # Minimum net score after friction
    ) -> None:
        self.risk_penalty_lambda = risk_penalty_lambda
        self.base_friction_bps = base_friction_bps
        self.top_k = top_k
        self.min_opportunity_score_bps = min_opportunity_score_bps

    def compute_opportunity_score(
        self,
        expected_return_bps: float,
        realized_vol_pct: float,
        spread_bps: Optional[float] = None,
    ) -> Tuple[float, float, float]:
        """
        Computes: Net Score = Expected Return (bps) - Estimated Friction (bps) - Lambda * Volatility (bps)
        """
        friction_bps = (spread_bps * 2.0 + 4.0) if spread_bps is not None else self.base_friction_bps
        vol_bps = realized_vol_pct * 10000.0
        vol_penalty = self.risk_penalty_lambda * vol_bps
        net_score = expected_return_bps - friction_bps - vol_penalty
        return round(net_score, 2), round(friction_bps, 2), round(vol_penalty, 2)

    def rank_universe_at_timestamp(
        self,
        timestamp: datetime,
        candidates: List[Dict[str, any]],
    ) -> List[RankedOpportunity]:
        """
        Ranks all candidate symbols evaluated at a single bar timestamp.
        Candidate dict contains: symbol, p_up, expected_return_bps, realized_vol_pct, spread_bps.
        """
        if not candidates:
            return []

        scored: List[dict] = []
        for c in candidates:
            exp_ret = c.get("expected_return_bps", 0.0)
            vol_pct = c.get("realized_vol_pct", 0.001)
            spread_bps = c.get("spread_bps", None)
            prob = c.get("p_up", 0.50)

            net_score, fric, vol_pen = self.compute_opportunity_score(
                expected_return_bps=exp_ret,
                realized_vol_pct=vol_pct,
                spread_bps=spread_bps,
            )
            scored.append({
                "symbol": c["symbol"],
                "raw_score": exp_ret,
                "expected_return_bps": exp_ret,
                "estimated_friction_bps": fric,
                "volatility_penalty_bps": vol_pen,
                "net_score": net_score,
                "confidence": prob,
            })

        # Sort descending by net opportunity score
        scored.sort(key=lambda x: x["net_score"], reverse=True)

        ranked: List[RankedOpportunity] = []
        for rank_idx, item in enumerate(scored):
            is_sel = (rank_idx < self.top_k) and (item["net_score"] >= self.min_opportunity_score_bps)
            ranked.append(
                RankedOpportunity(
                    timestamp=timestamp,
                    symbol=item["symbol"],
                    rank=rank_idx + 1,
                    raw_score=item["raw_score"],
                    expected_return_bps=item["expected_return_bps"],
                    estimated_friction_bps=item["estimated_friction_bps"],
                    volatility_penalty_bps=item["volatility_penalty_bps"],
                    net_opportunity_score=item["net_score"],
                    confidence=item["confidence"],
                    is_selected=is_sel,
                )
            )
        return ranked

    @staticmethod
    def evaluate_cross_sectional_ic(
        universe_predictions_df: pd.DataFrame,
        score_col: str = "net_opportunity_score",
        target_return_col: str = "target_future_return_6b",
    ) -> CrossSectionalEvaluation:
        """
        Evaluates Spearman Rank Information Coefficient (IC) and decile spreads across timestamps.
        """
        if universe_predictions_df.empty:
            return CrossSectionalEvaluation(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0)

        ics: List[float] = []
        top_decile_rets: List[float] = []
        bot_decile_rets: List[float] = []

        for ts, group in universe_predictions_df.groupby("timestamp"):
            if len(group) < 4:
                continue
            valid = group.dropna(subset=[score_col, target_return_col])
            if len(valid) < 4:
                continue

            scores = valid[score_col].values
            rets = valid[target_return_col].values

            # Spearman rank correlation
            corr, _ = spearmanr(scores, rets)
            if not np.isnan(corr):
                ics.append(float(corr))

            # Top vs bottom quantile returns
            n_q = max(1, len(valid) // 3)
            sorted_idx = np.argsort(scores)
            bot_ret = float(np.mean(rets[sorted_idx[:n_q]])) * 10000.0
            top_ret = float(np.mean(rets[sorted_idx[-n_q:]])) * 10000.0
            bot_decile_rets.append(bot_ret)
            top_decile_rets.append(top_ret)

        if not ics:
            return CrossSectionalEvaluation(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0)

        mean_ic = float(np.mean(ics))
        std_ic = float(np.std(ics, ddof=1)) if len(ics) > 1 else 1e-6
        t_stat = mean_ic / (std_ic / np.sqrt(len(ics)))
        ic_ir = mean_ic / std_ic

        top_mean = float(np.mean(top_decile_rets))
        bot_mean = float(np.mean(bot_decile_rets))
        spread = top_mean - bot_mean

        return CrossSectionalEvaluation(
            mean_spearman_ic=round(mean_ic, 4),
            ic_t_stat=round(t_stat, 2),
            ic_ir=round(ic_ir, 4),
            top_decile_return_bps=round(top_mean, 2),
            bottom_decile_return_bps=round(bot_mean, 2),
            long_short_spread_bps=round(spread, 2),
            total_timestamps_evaluated=len(ics),
        )
