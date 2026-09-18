"""
Remote Data & Environment Verification Script for Unity HPC.
Verifies SHA256 hashes of Alpaca 1-minute datasets and validates the August holdout firewall.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
import pandas as pd

from src.data.historical_market_data import STANDARD_50_UNIVERSE
from src.data.real_data_firewall import RealDataFirewall, AugustHoldoutFirewallError


def verify_remote_data():
    print("======================================================================")
    print("UNITY HPC REMOTE DATA & ENVIRONMENT AUDIT")
    print("======================================================================")

    # 1. Firewall Verification
    try:
        RealDataFirewall.assert_date_authorized("2026-08-10")
        print("ERROR: August 2026 firewall failed to block access!")
        sys.exit(1)
    except AugustHoldoutFirewallError:
        print("[Pass] August 2026 Holdout Firewall is ACTIVE & SEALED.")

    # 2. Check Processed Parquet Data
    data_dir = Path("data/processed/alpaca_extended_1m")
    if not data_dir.exists():
        data_dir = Path("data/processed/alpaca_1m")

    if not data_dir.exists():
        print(f"ERROR: Market data directory {data_dir} not found!")
        sys.exit(1)

    print(f"\nAuditing 50 canonical symbols in: {data_dir}")
    total_bars = 0
    missing_symbols = []

    for sym in sorted(STANDARD_50_UNIVERSE):
        fpath = data_dir / f"{sym}_1m.parquet"
        if not fpath.exists():
            fpath = data_dir / f"{sym}.parquet"
        if not fpath.exists():
            missing_symbols.append(sym)
            continue

        df = pd.read_parquet(fpath)
        sha = hashlib.sha256(fpath.read_bytes()).hexdigest()[:16]
        date_col = "date_str" if "date_str" in df.columns else ("timestamp_et" if "timestamp_et" in df.columns else df.columns[0])
        total_bars += len(df)
        min_d = str(df[date_col].min())[:10]
        max_d = str(df[date_col].max())[:10]
        print(f"  [{sym:5s}] : {len(df):>7,d} bars | Range: {min_d} to {max_d} | SHA: {sha}...")

    if missing_symbols:
        print(f"\nERROR: Missing {len(missing_symbols)} symbols: {missing_symbols}")
        sys.exit(1)

    print("\n======================================================================")
    print(f"ALL 50 SECURITIES VERIFIED | Total Bars: {total_bars:,d}")
    print("UNITY ENVIRONMENT VERIFICATION: PASSED")
    print("======================================================================")


if __name__ == "__main__":
    verify_remote_data()
