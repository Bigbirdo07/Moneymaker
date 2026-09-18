"""
FastScanner Architecture & Premarket Filter Engine (Phase B).
Quickly filters 500-1,500 eligible liquid stocks down to 50-100 high-conviction
candidates for full multi-horizon inference while ensuring high winner recall.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class ScoredCandidate:
    """Fast-scanner score summary for a symbol."""
    symbol: str
    scanner_score: float
    relative_volume_score: float
    momentum_score: float
    vwap_distance_score: float
    rank: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "scanner_score": round(self.scanner_score, 4),
            "relative_volume_score": round(self.relative_volume_score, 4),
            "momentum_score": round(self.momentum_score, 4),
            "vwap_distance_score": round(self.vwap_distance_score, 4),
            "rank": self.rank,
        }


class FastScanner:
    """
    Lightweight, low-latency premarket and intraday opportunity scanner.
    """

    def __init__(
        self,
        top_k_candidates: int = 50,
        min_momentum_bps: float = 5.0,
        rel_vol_weight: float = 0.35,
        momentum_weight: float = 0.45,
        vwap_weight: float = 0.20,
    ) -> None:
        self.top_k_candidates = top_k_candidates
        self.min_momentum_bps = min_momentum_bps
        self.rel_vol_weight = rel_vol_weight
        self.momentum_weight = momentum_weight
        self.vwap_weight = vwap_weight

    def scan_universe(self, df_cross_section: pd.DataFrame) -> List[ScoredCandidate]:
        """
        Ranks eligible symbols in df_cross_section and returns Top-K candidates.
        """
        if df_cross_section.empty:
            return []

        df = df_cross_section.copy()

        # Extract or compute normalized metrics
        mom_15m = df.get("ret_15m_bps", pd.Series(0.0, index=df.index))
        rel_vol = df.get("rel_vol_5d", pd.Series(1.0, index=df.index))
        vwap_dist = df.get("dist_vwap_bps", pd.Series(0.0, index=df.index))

        # Cross-sectional percentile ranking [0, 1]
        mom_rank = mom_15m.rank(pct=True)
        vol_rank = rel_vol.rank(pct=True)
        vwap_rank = vwap_dist.rank(pct=True)

        combined_score = (
            (self.momentum_weight * mom_rank) +
            (self.rel_vol_weight * vol_rank) +
            (self.vwap_weight * vwap_rank)
        )

        df["scanner_score"] = combined_score
        df["mom_score"] = mom_rank
        df["vol_score"] = vol_rank
        df["vwap_score"] = vwap_rank

        sorted_df = df.sort_values(by="scanner_score", ascending=False).reset_index(drop=True)
        top_slice = sorted_df.head(self.top_k_candidates)

        candidates = []
        for idx, row in top_slice.iterrows():
            candidates.append(ScoredCandidate(
                symbol=str(row["symbol"]),
                scanner_score=float(row["scanner_score"]),
                relative_volume_score=float(row["vol_score"]),
                momentum_score=float(row["mom_score"]),
                vwap_distance_score=float(row["vwap_score"]),
                rank=idx + 1,
            ))

        return candidates
