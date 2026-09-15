"""Security archetype characterization, cross-sectional clustering, and NVDA effect analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class SymbolProfile:
    """Quantitative statistical profile of an individual security."""
    symbol: str
    sector: str
    beta_to_spy: float
    annualized_volatility_pct: float
    atr_pct: float
    median_spread_bps: float
    average_daily_volume: float
    rvol_std: float
    archetype: str
    net_strategy_return_pct: float = 0.0
    win_rate_pct: float = 0.0
    total_trades: int = 0


class SecurityArchetypeAnalyzer:
    """Characterizes securities into quantitative archetypes to audit performance drivers."""

    @staticmethod
    def profile_symbol(
        symbol_df: pd.DataFrame,
        spy_df: Optional[pd.DataFrame] = None,
        sector: str = "UNKNOWN",
    ) -> SymbolProfile:
        """Computes statistical risk and liquidity metrics for a symbol."""
        close = symbol_df["close"].values
        returns = symbol_df["close"].pct_change().dropna().values
        vol = float(np.std(returns, ddof=1)) * np.sqrt(252.0 * 78.0) * 100.0
        
        atr = symbol_df["feature_atr_pct"].mean() * 100.0 if "feature_atr_pct" in symbol_df else 0.5
        spread = symbol_df["spread"].median() / symbol_df["close"].median() * 10000.0 if "spread" in symbol_df else 1.5
        adv = float(symbol_df["volume"].sum() / max(1, len(symbol_df) / 78.0)) if "volume" in symbol_df else 1000000.0
        rvol_std = float(symbol_df["feature_relative_volume_20b"].std()) if "feature_relative_volume_20b" in symbol_df else 0.5

        # Beta calculation to SPY
        beta = 1.0
        if spy_df is not None and not spy_df.empty:
            spy_ret = spy_df["close"].pct_change().dropna().values
            min_l = min(len(returns), len(spy_ret))
            if min_l > 20:
                cov = np.cov(returns[:min_l], spy_ret[:min_l])[0, 1]
                var_spy = np.var(spy_ret[:min_l])
                beta = float(cov / (var_spy + 1e-8))

        # Assign Archetype
        if beta > 1.30 and vol > 25.0:
            archetype = "HIGH_BETA_HIGH_VOL"
        elif beta > 1.0 and vol <= 25.0:
            archetype = "HIGH_BETA_LOW_VOL"
        elif beta <= 0.85 and vol < 20.0:
            archetype = "DEFENSIVE"
        elif sector == "financials":
            archetype = "FINANCIAL"
        elif sector == "energy":
            archetype = "ENERGY"
        else:
            archetype = "STANDARD_LARGE_CAP"

        return SymbolProfile(
            symbol=str(symbol_df["symbol"].iloc[0]),
            sector=sector,
            beta_to_spy=round(beta, 2),
            annualized_volatility_pct=round(vol, 2),
            atr_pct=round(atr, 2),
            median_spread_bps=round(spread, 2),
            average_daily_volume=round(adv, 0),
            rvol_std=round(rvol_std, 2),
            archetype=archetype,
        )

    @classmethod
    def evaluate_archetype_generalization(
        cls,
        profiles: List[SymbolProfile],
    ) -> pd.DataFrame:
        """Aggregates strategy performance and sample counts across security archetypes."""
        records = []
        df = pd.DataFrame([p.__dict__ for p in profiles])
        for arch, group in df.groupby("archetype"):
            records.append({
                "archetype": arch,
                "symbols_count": len(group),
                "symbols": ", ".join(group["symbol"].tolist()),
                "mean_beta": round(float(group["beta_to_spy"].mean()), 2),
                "mean_volatility_pct": round(float(group["annualized_volatility_pct"].mean()), 2),
                "mean_net_return_pct": round(float(group["net_strategy_return_pct"].mean()), 2),
                "mean_win_rate_pct": round(float(group["win_rate_pct"].mean()), 2),
                "total_trades": int(group["total_trades"].sum()),
            })
        return pd.DataFrame(records)
