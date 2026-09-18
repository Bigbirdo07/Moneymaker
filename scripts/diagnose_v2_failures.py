"""
Diagnostic Script to Analyze Engine V2 Failures and Loss Distributions
"""
import pandas as pd
import numpy as np
from pathlib import Path

def main():
    p_path = Path("/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/artifacts/unity/phase11a/PHASE11A_20260917_191238/PHASE_11A_MONTHLY_RESULTS.parquet")
    if not p_path.exists():
        p_path = Path("artifacts/unity/phase11a/PHASE11A_20260917_191238/PHASE_11A_MONTHLY_RESULTS.parquet")
    
    df = pd.read_parquet(p_path)
    print(f"Total Phase 11A Trades: {len(df)}")
    print(f"Columns: {df.columns.tolist()}\n")
    
    print("=== MONTHLY NET PNL & WIN RATE ===")
    m_grp = df.groupby("month_id")["net_pnl"].agg(
        count="count",
        sum="sum",
        mean="mean",
        win_rate=lambda x: (x > 0).mean()
    )
    print(m_grp.to_string())
    
    print("\n=== LOSS REASONS BREAKDOWN ===")
    losses = df[df["net_pnl"] < 0]
    l_grp = losses.groupby("exit_reason")["net_pnl"].agg(
        count="count",
        sum="sum",
        mean="mean"
    ).sort_values(by="sum")
    print(l_grp.to_string())
    
    print("\n=== SECTOR LOSSES & WINS ===")
    s_grp = df.groupby("sector")["net_pnl"].agg(
        count="count",
        sum="sum",
        win_rate=lambda x: (x > 0).mean()
    ).sort_values(by="sum", ascending=False)
    print(s_grp.to_string())
    
    print("\n=== NOV & DEC 2025 DETAILED FORENSICS ===")
    nov_dec = df[df["month_id"].isin(["2025-11", "2025-12"])]
    print(f"Nov-Dec Trades: {len(nov_dec)}, Net PnL: ${nov_dec['net_pnl'].sum():.2f}")
    print(nov_dec.groupby("exit_reason")["net_pnl"].agg(["count", "sum", "mean"]))
    print("\nNov-Dec Trades Table:")
    print(nov_dec[["trade_id", "symbol", "session_date", "entry_price", "exit_price", "gross_pnl", "net_pnl", "total_friction", "bars_held", "exit_reason"]].to_string())

if __name__ == "__main__":
    main()
