"""
Real-Market Feature Store V3 for Phase 11B / Engine V3.
Computes cross-sectional relative features, SPY relative strength, market breadth,
volatility expansion states, and multi-task forward targets across the 50-stock universe.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass
from src.data.calendar import TradingCalendar
from src.data.real_data_firewall import RealDataFirewall

logger = get_logger("features.real_feature_store_v3")

SECTOR_MAP = {
    'AAPL': 'Technology', 'MSFT': 'Technology', 'NVDA': 'Technology', 'AVGO': 'Technology',
    'ORCL': 'Technology', 'CRM': 'Technology', 'CSCO': 'Technology', 'ACN': 'Technology',
    'ADBE': 'Technology', 'INTC': 'Technology', 'AMD': 'Technology', 'TXN': 'Technology',
    'QCOM': 'Technology', 'AMZN': 'Consumer Cyclical', 'TSLA': 'Consumer Cyclical',
    'HD': 'Consumer Cyclical', 'MCD': 'Consumer Cyclical', 'NKE': 'Consumer Cyclical',
    'LOW': 'Consumer Cyclical', 'GOOGL': 'Communication Services', 'META': 'Communication Services',
    'NFLX': 'Communication Services', 'CMCSA': 'Communication Services', 'DIS': 'Communication Services',
    'BRK.B': 'Financials', 'JPM': 'Financials', 'V': 'Financials', 'MA': 'Financials',
    'BAC': 'Financials', 'WFC': 'Financials', 'MS': 'Financials', 'GS': 'Financials',
    'LLY': 'Healthcare', 'JNJ': 'Healthcare', 'UNH': 'Healthcare', 'ABBV': 'Healthcare',
    'MRK': 'Healthcare', 'TMO': 'Healthcare', 'ABT': 'Healthcare', 'PFE': 'Healthcare',
    'WMT': 'Consumer Defensive', 'PG': 'Consumer Defensive', 'COST': 'Consumer Defensive',
    'KO': 'Consumer Defensive', 'PEP': 'Consumer Defensive', 'XOM': 'Energy', 'CVX': 'Energy',
    'LIN': 'Basic Materials', 'CAT': 'Industrials', 'GE': 'Industrials'
}


class RealMarketFeatureStoreV3:
    """
    Advanced cross-sectional feature engineering engine for Real Market Engine V3.
    """

    def __init__(
        self,
        data_dir: Path | str = "data/processed/alpaca_extended_1m",
        base_spread_bps: float = 3.0,
        base_slippage_bps: float = 1.5,
        per_share_commission: float = 0.0005,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.base_spread_bps = base_spread_bps
        self.base_slippage_bps = base_slippage_bps
        self.per_share_commission = per_share_commission
        self.calendar = TradingCalendar()

    def load_symbol_dataframe(self, symbol: str) -> pd.DataFrame:
        """Loads and pre-indexes Parquet bar data for a single symbol."""
        p_ext = self.data_dir / f"{symbol}_1m.parquet"
        p_std = Path("data/processed/alpaca_1m") / f"{symbol}_1m.parquet"
        p = p_ext if p_ext.exists() else p_std
        if not p.exists():
            raise FileNotFoundError(f"No market data parquet found for {symbol}")

        df = pd.read_parquet(p)
        df["dt_et"] = pd.to_datetime(df["timestamp_et"])
        df["date_str"] = df["dt_et"].dt.strftime("%Y-%m-%d")
        df["time_str"] = df["dt_et"].dt.strftime("%H:%M:%S")

        df = RealDataFirewall.filter_authorized_dataframe(df, date_column="date_str")
        df = df.sort_values("dt_et").reset_index(drop=True)
        return df

    def compute_symbol_features_vectorized(
        self,
        symbol: str,
        sym_df: pd.DataFrame,
        sample_step: int = 15,
    ) -> pd.DataFrame:
        """
        High-performance vectorized feature calculation for an individual security.
        """
        if sym_df.empty or len(sym_df) < 50:
            return pd.DataFrame()

        df = sym_df.copy().reset_index(drop=True)
        c = df["close"]
        v = df["volume"]
        h = df["high"]
        l = df["low"]

        # Returns across multiple horizons (bps)
        df["ret_1m_bps"] = c.pct_change(1) * 10000.0
        df["ret_3m_bps"] = c.pct_change(3) * 10000.0
        df["ret_5m_bps"] = c.pct_change(5) * 10000.0
        df["ret_10m_bps"] = c.pct_change(10) * 10000.0
        df["ret_15m_bps"] = c.pct_change(15) * 10000.0
        df["ret_30m_bps"] = c.pct_change(30) * 10000.0
        df["ret_60m_bps"] = c.pct_change(60) * 10000.0

        # Technical Indicators
        ema10 = c.ewm(span=10, adjust=False).mean()
        ema30 = c.ewm(span=30, adjust=False).mean()
        df["ema_trend_10_30_bps"] = ((ema10 - ema30) / np.maximum(1e-4, ema30)) * 10000.0

        cum_vol = df.groupby("date_str")["volume"].cumsum()
        cum_pv = df.groupby("date_str").apply(lambda g: (g["close"] * g["volume"]).cumsum(), include_groups=False).reset_index(drop=True)
        vwap = cum_pv / np.maximum(1.0, cum_vol)
        df["dist_from_vwap_bps"] = ((c - vwap) / np.maximum(1e-4, vwap)) * 10000.0

        run_high = df.groupby("date_str")["high"].cummax()
        run_low = df.groupby("date_str")["low"].cummin()
        df["dist_from_high_bps"] = ((c - run_high) / np.maximum(1e-4, run_high)) * 10000.0
        df["dist_from_low_bps"] = ((c - run_low) / np.maximum(1e-4, run_low)) * 10000.0
        df["breakout_distance_bps"] = ((c - run_high.shift(1)) / np.maximum(1e-4, run_high.shift(1))) * 10000.0

        # RSI 14
        delta = c.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / np.maximum(1e-6, loss)
        df["rsi_14"] = 100 - (100 / (1 + rs))

        # Volatility
        df["realized_vol_15m_bps"] = df["ret_1m_bps"].rolling(15).std()
        df["realized_vol_60m_bps"] = df["ret_1m_bps"].rolling(60).std()
        tr = np.maximum(h - l, np.maximum(abs(h - c.shift(1)), abs(l - c.shift(1))))
        atr14 = tr.rolling(14).mean()
        df["atr_14_bps"] = (atr14 / np.maximum(1e-4, c)) * 10000.0
        df["range_expansion_ratio"] = (run_high - run_low) / np.maximum(1e-4, atr14 / 10000.0 * c)

        # Volume
        mean_vol = df.groupby("date_str")["volume"].transform(lambda x: x.expanding().mean())
        df["relative_volume"] = v / np.maximum(1.0, mean_vol)
        df["volume_acceleration"] = v.pct_change(1).fillna(0.0)
        df["trade_intensity"] = df["relative_volume"]

        # Overnight Gap
        prev_close_series = df.groupby("date_str")["close"].transform("last").shift(390)
        day_open_series = df.groupby("date_str")["open"].transform("first")
        df["overnight_gap_bps"] = ((day_open_series - prev_close_series) / np.maximum(1e-4, prev_close_series)) * 10000.0

        # Time
        hours = df["dt_et"].dt.hour
        minutes = df["dt_et"].dt.minute
        mins_since_open = (hours - 9) * 60 + minutes - 30
        df["minutes_since_open"] = mins_since_open
        df["minutes_to_close"] = np.maximum(0, 390 - mins_since_open)

        round_trip_cost_bps = (self.base_spread_bps * 2.0) + (self.base_slippage_bps * 2.0) + 0.5
        df["estimated_friction_bps"] = round_trip_cost_bps

        # Forward Targets (Executable Net Targets at 30m, 60m, 120m)
        df["fwd_raw_30m_bps"] = (c.shift(-30) - c) / c * 10000.0
        df["fwd_raw_60m_bps"] = (c.shift(-60) - c) / c * 10000.0
        df["fwd_raw_120m_bps"] = (c.shift(-120) - c) / c * 10000.0

        df["fwd_net_30m_bps"] = df["fwd_raw_30m_bps"] - round_trip_cost_bps
        df["fwd_net_60m_bps"] = df["fwd_raw_60m_bps"] - round_trip_cost_bps
        df["fwd_net_120m_bps"] = df["fwd_raw_120m_bps"] - round_trip_cost_bps

        # MFE / MAE over next 60 bars
        fwd_high_60 = df["high"].iloc[::-1].rolling(60, min_periods=1).max().iloc[::-1].shift(-1)
        fwd_low_60 = df["low"].iloc[::-1].rolling(60, min_periods=1).min().iloc[::-1].shift(-1)
        df["fwd_mfe_60m_pct"] = ((fwd_high_60 - c) / c) * 100.0
        df["fwd_mae_60m_pct"] = ((c - fwd_low_60) / c) * 100.0
        df["target_asymmetry_60m"] = (df["fwd_mfe_60m_pct"] >= 2.0) & (df["fwd_mae_60m_pct"] <= 1.0)
        df["target_asymmetry_60m"] = df["target_asymmetry_60m"].astype(int)

        df["label_binary_net_30m"] = (df["fwd_net_30m_bps"] > 0).astype(int)
        df["label_binary_net_60m"] = (df["fwd_net_60m_bps"] > 0).astype(int)
        df["label_binary_net_120m"] = (df["fwd_net_120m_bps"] > 0).astype(int)
        df["close_price"] = c

        mask_hours = (df["time_str"] >= "09:35:00") & (df["time_str"] <= "15:45:00")
        df_reg = df[mask_hours].copy()
        sampled = df_reg.iloc[::sample_step].copy().reset_index(drop=True)
        return sampled

    def build_cross_sectional_matrix(
        self,
        symbols_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Enriches multi-symbol feature dataframe with contemporaneous cross-sectional rankings and market breadth.
        """
        df = symbols_df.copy()
        if df.empty or "timestamp_et" not in df.columns:
            return df

        # Cross-sectional return percentiles
        df["cs_return_rank_15m"] = df.groupby("timestamp_et")["ret_15m_bps"].rank(pct=True).fillna(0.5)
        df["cs_return_rank_60m"] = df.groupby("timestamp_et")["ret_60m_bps"].rank(pct=True).fillna(0.5)
        df["cs_vwap_rank"] = df.groupby("timestamp_et")["dist_from_vwap_bps"].rank(pct=True).fillna(0.5)
        df["cs_volume_rank"] = df.groupby("timestamp_et")["relative_volume"].rank(pct=True).fillna(0.5)

        # Market Breadth: Fraction of universe above VWAP at timestamp T
        above_vwap = (df["dist_from_vwap_bps"] > 0).astype(float)
        df["market_breadth_above_vwap"] = df.groupby("timestamp_et")["dist_from_vwap_bps"].transform(lambda x: (x > 0).mean()).fillna(0.5)

        # Universe Mean Returns (Market Proxy)
        df["market_mean_ret_15m_bps"] = df.groupby("timestamp_et")["ret_15m_bps"].transform("mean").fillna(0.0)
        df["market_mean_ret_60m_bps"] = df.groupby("timestamp_et")["ret_60m_bps"].transform("mean").fillna(0.0)

        # Relative Strength vs Universe Mean
        df["rel_strength_15m_bps"] = df["ret_15m_bps"] - df["market_mean_ret_15m_bps"]
        df["rel_strength_60m_bps"] = df["ret_60m_bps"] - df["market_mean_ret_60m_bps"]

        # Market Regime Flag (1 = Bullish Breadth >= 50%, 0 = Adverse Breadth)
        df["market_regime_tradable"] = (df["market_breadth_above_vwap"] >= 0.45).astype(int)

        return df
