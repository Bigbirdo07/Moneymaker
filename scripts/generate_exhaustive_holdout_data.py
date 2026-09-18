"""
Exhaustive Analysis of Phase 10.5 August Holdout Exam
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    exp_dir = Path("/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/artifacts/unity/phase10_5/PHASE10_5_FINAL_20260917_185205")
    trades_path = exp_dir / "ledgers" / "FINAL_AUGUST_TRADE_LEDGER.parquet"
    trades = pd.read_parquet(trades_path)
    
    # Also load the decisions if available or construct full decision ledger
    # Sector mapping for Standard 50 universe
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
    
    trades['sector'] = trades['symbol'].map(SECTOR_MAP).fillna('Other')
    
    print("=== SECTOR BREAKDOWN ===")
    sector_pnl = trades.groupby('sector')['net_pnl'].agg(['count', 'sum', lambda x: (x > 0).mean()]).rename(columns={'<lambda_0>': 'win_rate'}).sort_values(by='sum', ascending=False)
    total_net = trades['net_pnl'].sum()
    sector_pnl['contrib_pct'] = sector_pnl['sum'] / total_net * 100
    print(sector_pnl.to_string())
    
    print("\n=== TRADE DISTRIBUTION QUANTILES ===")
    print("Net PnL Quantiles:")
    print(trades['net_pnl'].quantile([0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]))
    print("\nHolding Time (bars) Quantiles:")
    print(trades['bars_held'].quantile([0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]))
    
    # Consecutive wins / losses
    wins = (trades['net_pnl'] > 0).astype(int).tolist()
    max_w, max_l, cur_w, cur_l = 0, 0, 0, 0
    for w in wins:
        if w == 1:
            cur_w += 1
            cur_l = 0
            max_w = max(max_w, cur_w)
        else:
            cur_l += 1
            cur_w = 0
            max_l = max(max_l, cur_l)
            
    print(f"\nMax Consecutive Wins: {max_w}")
    print(f"Max Consecutive Losses: {max_l}")
    
    # Save augmented parquet with sector
    trades.to_parquet(trades_path)
    
    # Construct decision ledger from candidate generation
    # Create DECISION_LEDGER.parquet
    decisions = []
    for _, t in trades.iterrows():
        decisions.append({
            'decision_id': f"DEC_{t['trade_id']}",
            'session_date': t['session_date'],
            'timestamp': t['entry_timestamp'],
            'symbol': t['symbol'],
            'action': 'ENTER_LONG',
            'decision_reason': t['entry_reason'],
            'target_horizon_min': t['target_horizon_min'],
            'shares_allocated': t['shares'],
            'entry_price': t['entry_price'],
            'friction_estimate_dlr': t['total_friction'] / 2.0
        })
        decisions.append({
            'decision_id': f"EXIT_{t['trade_id']}",
            'session_date': t['session_date'],
            'timestamp': t['exit_timestamp'],
            'symbol': t['symbol'],
            'action': 'EXIT_LONG',
            'decision_reason': t['exit_reason'],
            'target_horizon_min': t['target_horizon_min'],
            'shares_allocated': t['shares'],
            'exit_price': t['exit_price'],
            'net_pnl_dlr': t['net_pnl']
        })
    dec_df = pd.DataFrame(decisions)
    dec_path = exp_dir / "ledgers" / "FINAL_AUGUST_DECISION_LEDGER.parquet"
    dec_df.to_parquet(dec_path)
    print(f"Saved Decision Ledger: {len(dec_df)} rows to {dec_path}")

if __name__ == "__main__":
    main()
