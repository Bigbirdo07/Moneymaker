"""
Premarket Opportunity Scanner for Historical Replay & Autonomous Research.
Evaluates cross-sectional candidates between 08:30 and 09:15 ET using only visible premarket data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass
from src.replay.market_replay_engine import HistoricalMarketReplayEngine

logger = get_logger("signals.premarket_scanner")


@dataclass
class PremarketCandidate:
    """Ranked premarket candidate evaluated before regular market open."""
    symbol: str
    timestamp: str
    premarket_return_bps: float
    premarket_volume: float
    relative_volume: float
    gap_from_prev_close_bps: float
    realized_vol_bps: float
    atr_vol_bps: float
    estimated_spread_bps: float
    alpha_a_score: float
    alpha_b_score: float
    ensemble_score: float
    expected_gross_return_bps: float
    expected_cost_bps: float
    expected_net_edge_bps: float
    liquidity_score: float
    risk_score: float
    candidate_rank: int
    is_eligible: bool
    evidence_class: str = EvidenceClass.HISTORICAL_REPLAY.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PremarketOpportunityScanner:
    """
    Scans universe during 08:30–09:15 ET using only leakage-safe visible data
    to extract technical, microstructure, and alpha signals for morning allocation.
    """

    def __init__(
        self,
        min_premarket_volume: float = 500.0,
        min_expected_net_edge_bps: float = 3.0,
        max_spread_bps: float = 25.0,
        top_candidates_limit: int = 10,
    ) -> None:
        self.min_premarket_volume = min_premarket_volume
        self.min_expected_net_edge_bps = min_expected_net_edge_bps
        self.max_spread_bps = max_spread_bps
        self.top_candidates_limit = top_candidates_limit

    def scan_universe(
        self,
        replay_engine: HistoricalMarketReplayEngine,
        symbols: List[str],
    ) -> List[PremarketCandidate]:
        """
        Executes premarket scan at current replay_engine.simulated_clock.
        Returns sorted list of candidates, or empty list (NO_VALID_CANDIDATES).
        """
        clock = replay_engine.simulated_clock
        clock_iso = clock.isoformat()
        candidates: List[PremarketCandidate] = []

        for sym in symbols:
            vis_bars = replay_engine.get_visible_bars(sym, lookback_bars=120)
            if len(vis_bars) < 5:
                continue

            # Ensure leakage assertion
            replay_engine.assert_no_future_leakage(vis_bars["timestamp"])

            # Premarket bars for today
            today_et = vis_bars["timestamp"].dt.tz_convert("America/New_York").dt.date.iloc[-1]
            is_today = vis_bars["timestamp"].dt.tz_convert("America/New_York").dt.date == today_et
            today_bars = vis_bars[is_today].copy()
            prev_bars = vis_bars[~is_today].copy()

            if today_bars.empty:
                continue

            curr_price = float(today_bars["close"].iloc[-1])
            pm_open = float(today_bars["open"].iloc[0])
            pm_ret_bps = ((curr_price - pm_open) / pm_open) * 10000.0
            pm_vol = float(today_bars["volume"].sum())

            # Prior close
            if not prev_bars.empty:
                prev_close = float(prev_bars["close"].iloc[-1])
                gap_bps = ((curr_price - prev_close) / prev_close) * 10000.0
            else:
                gap_bps = 0.0

            # Realized Volatility over visible bars
            rets = vis_bars["close"].pct_change().dropna()
            realized_vol = float(rets.std()) if len(rets) > 1 else 0.001
            realized_vol_bps = realized_vol * 10000.0

            # ATR Volatility Proxy
            tr = np.maximum(
                vis_bars["high"] - vis_bars["low"],
                np.maximum(
                    np.abs(vis_bars["high"] - vis_bars["close"].shift(1)),
                    np.abs(vis_bars["low"] - vis_bars["close"].shift(1))
                )
            ).dropna()
            atr_val = float(tr.mean()) if len(tr) > 0 else (curr_price * 0.005)
            atr_bps = (atr_val / curr_price) * 10000.0

            # Microstructure & Spread
            spread_val = float(today_bars["spread"].iloc[-1]) if "spread" in today_bars else (curr_price * 0.0003)
            spread_bps = (spread_val / curr_price) * 10000.0

            # Alpha proxies (Alpha A: Mean Reversion / Microstructure, Alpha B: Momentum / Gap continuation)
            alpha_a_score = float(np.tanh(-pm_ret_bps / 50.0))  # Reversion score
            alpha_b_score = float(np.tanh((gap_bps + pm_ret_bps * 0.5) / 40.0)) # Momentum / Gap score
            ensemble_score = float(0.40 * alpha_a_score + 0.60 * alpha_b_score)

            # Expected Gross Return & Costs
            exp_gross_return_bps = ensemble_score * 25.0  # Normalized forecast in bps
            estimated_cost_bps = spread_bps * 2.0 + 3.0   # Round-trip spread + slippage proxy
            expected_net_edge_bps = exp_gross_return_bps - estimated_cost_bps

            # Relative volume
            avg_bar_vol = float(vis_bars["volume"].mean()) if len(vis_bars) > 0 else 1000.0
            rel_vol = float(pm_vol / (avg_bar_vol * max(1, len(today_bars))))

            # Liquidity & Risk Scores
            liq_score = min(1.0, pm_vol / 10000.0)
            risk_score = (realized_vol_bps / 100.0) + (spread_bps / 10.0)

            is_elig = (
                pm_vol >= self.min_premarket_volume and
                spread_bps <= self.max_spread_bps and
                expected_net_edge_bps >= self.min_expected_net_edge_bps
            )

            candidates.append(PremarketCandidate(
                symbol=sym,
                timestamp=clock_iso,
                premarket_return_bps=round(pm_ret_bps, 2),
                premarket_volume=round(pm_vol, 1),
                relative_volume=round(rel_vol, 2),
                gap_from_prev_close_bps=round(gap_bps, 2),
                realized_vol_bps=round(realized_vol_bps, 2),
                atr_vol_bps=round(atr_bps, 2),
                estimated_spread_bps=round(spread_bps, 2),
                alpha_a_score=round(alpha_a_score, 4),
                alpha_b_score=round(alpha_b_score, 4),
                ensemble_score=round(ensemble_score, 4),
                expected_gross_return_bps=round(exp_gross_return_bps, 2),
                expected_cost_bps=round(estimated_cost_bps, 2),
                expected_net_edge_bps=round(expected_net_edge_bps, 2),
                liquidity_score=round(liq_score, 3),
                risk_score=round(risk_score, 3),
                candidate_rank=0,
                is_eligible=is_elig,
            ))

        # Sort descending by expected net edge
        candidates.sort(key=lambda x: x.expected_net_edge_bps, reverse=True)

        for rank_idx, c in enumerate(candidates):
            c.candidate_rank = rank_idx + 1

        return candidates[:self.top_candidates_limit]
