"""
Incremental Forward Feature Calculation Engine for Phase 3A Shadow Trading.
Computes technical and microstructure features strictly from historical completed bars
and current top-of-book quotes without future lookahead or retrospective reconstruction.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from src.data.market_provider import BarEvent, QuoteEvent


class IncrementalFeatureEngine:
    """Computes leakage-safe features incrementally on each live decision cycle."""

    @staticmethod
    def compute_features(
        symbol_bars: List[BarEvent],
        current_quote: QuoteEvent,
        market_benchmark_bars: Optional[List[BarEvent]] = None,
    ) -> Dict[str, float]:
        """
        Compute feature vector for a symbol given its historical bars and current quote.
        Guarantees: Uses strictly past finalized bars + current quote.
        """
        if len(symbol_bars) < 14:
            raise ValueError(f"Insufficient historical bars: {len(symbol_bars)} (minimum 14 required)")

        closes = np.array([b.close for b in symbol_bars])
        highs = np.array([b.high for b in symbol_bars])
        lows = np.array([b.low for b in symbol_bars])
        volumes = np.array([b.volume for b in symbol_bars])

        # 1. Momentum Returns
        ret_5m = (closes[-1] / closes[-2] - 1.0) if len(closes) >= 2 else 0.0
        ret_15m = (closes[-1] / closes[-4] - 1.0) if len(closes) >= 4 else ret_5m
        ret_30m = (closes[-1] / closes[-7] - 1.0) if len(closes) >= 7 else ret_15m

        # 2. Realized Volatility (14-bar return standard deviation)
        bar_returns = np.diff(closes[-15:]) / closes[-15:-1]
        volatility_14 = float(np.std(bar_returns)) if len(bar_returns) > 1 else 0.001

        # 3. Average True Range (ATR)
        tr_list = []
        for i in range(1, min(15, len(symbol_bars))):
            tr = max(
                highs[-i] - lows[-i],
                abs(highs[-i] - closes[-i - 1]),
                abs(lows[-i] - closes[-i - 1]),
            )
            tr_list.append(tr)
        atr_14 = float(np.mean(tr_list)) if tr_list else (highs[-1] - lows[-1])
        atr_pct = atr_14 / closes[-1] if closes[-1] > 0 else 0.0

        # 4. Relative Volume (RVOL 14)
        avg_vol_14 = float(np.mean(volumes[-14:])) if len(volumes) >= 14 else float(np.mean(volumes))
        rvol_14 = (volumes[-1] / avg_vol_14) if avg_vol_14 > 0 else 1.0

        # 5. VWAP Distance (bps)
        # Calculate intraday session VWAP
        cum_vol = np.sum(volumes[-14:])
        cum_pv = np.sum(closes[-14:] * volumes[-14:])
        rolling_vwap = (cum_pv / cum_vol) if cum_vol > 0 else closes[-1]
        vwap_distance_bps = ((closes[-1] - rolling_vwap) / rolling_vwap) * 10000.0

        # 6. Spread & Liquidity (bps)
        spread_bps = current_quote.spread_bps

        # 7. Benchmark Relative Momentum & Beta (if SPY bars provided)
        market_momentum_15m = 0.0
        relative_strength_15m = ret_15m
        if market_benchmark_bars and len(market_benchmark_bars) >= 4:
            spy_closes = np.array([b.close for b in market_benchmark_bars])
            market_momentum_15m = float(spy_closes[-1] / spy_closes[-4] - 1.0)
            relative_strength_15m = ret_15m - market_momentum_15m

        feature_dict = {
            "ret_5m": float(ret_5m),
            "ret_15m": float(ret_15m),
            "ret_30m": float(ret_30m),
            "volatility_14": float(volatility_14),
            "volatility_bps": float(volatility_14 * 10000.0),
            "atr_14": float(atr_14),
            "atr_pct": float(atr_pct),
            "rvol_14": float(rvol_14),
            "vwap_distance_bps": float(vwap_distance_bps),
            "spread_bps": float(spread_bps),
            "market_momentum_15m": float(market_momentum_15m),
            "relative_strength_15m": float(relative_strength_15m),
        }

        return feature_dict
