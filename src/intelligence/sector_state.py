"""
Sector State & Relative Momentum Engine (Phase E).

Computes sector-level premarket returns, breadth, relative volume,
and relative strength rankings.
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict
import numpy as np

from src.intelligence.morning_market_state import SectorPerformance


class SectorStateEngine:
    """
    Evaluates sector momentum and breadth across the eligible dynamic universe.
    """
    def __init__(self):
        pass

    def evaluate_sectors(
        self,
        symbol_returns_pct: Dict[str, float],
        symbol_sectors: Dict[str, str],
        symbol_rel_vol: Dict[str, float],
        spy_return_pct: float,
        fast_scanner_symbols: Optional[List[str]] = None,
    ) -> List[SectorPerformance]:
        scanner_set = set(fast_scanner_symbols or [])

        sector_symbols: Dict[str, List[str]] = defaultdict(list)
        for sym, sec in symbol_sectors.items():
            if sym in symbol_returns_pct:
                sector_symbols[sec].append(sym)

        results: List[SectorPerformance] = []

        for sec, syms in sector_symbols.items():
            if not syms:
                continue
            rets = [symbol_returns_pct[s] for s in syms]
            rvol = [symbol_rel_vol.get(s, 1.0) for s in syms]
            
            avg_ret = float(np.mean(rets))
            rel_ret_bps = (avg_ret - spy_return_pct) * 100.0
            pos_count = sum(1 for r in rets if r > 0.0)
            breadth_pct = (pos_count / len(syms)) * 100.0 if syms else 0.0
            avg_rvol = float(np.mean(rvol))
            scanner_survivors = sum(1 for s in syms if s in scanner_set)

            results.append(SectorPerformance(
                sector=sec,
                premarket_return_pct=avg_ret,
                relative_return_vs_spy_bps=rel_ret_bps,
                breadth_pct_positive=breadth_pct,
                relative_volume=avg_rvol,
                eligible_symbol_count=len(syms),
                scanner_survivor_count=scanner_survivors,
            ))

        # Sort by relative return vs SPY descending
        results.sort(key=lambda x: x.relative_return_vs_spy_bps, reverse=True)
        return results
