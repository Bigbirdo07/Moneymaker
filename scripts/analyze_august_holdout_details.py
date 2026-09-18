"""
Analyze August 2026 Holdout Results in Detail
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    exp_dir = Path("artifacts/unity/phase10_5/PHASE10_5_FINAL_20260917_185205")
    trades_path = exp_dir / "ledgers" / "FINAL_AUGUST_TRADE_LEDGER.parquet"
    if not trades_path.exists():
        trades_path = Path("/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM") / trades_path
    
    trades = pd.read_parquet(trades_path)
    total_net = float(trades['net_pnl'].sum())
    total_gross = float(trades['gross_pnl'].sum())
    total_friction = float(trades['total_friction'].sum())
    n_trades = len(trades)
    
    print("======================================================================")
    print(f"AUGUST 2026 HOLDOUT ANALYSIS: {n_trades} TRADES")
    print(f"Gross PnL: ${total_gross:.2f} | Net PnL: ${total_net:.2f} | Friction: ${total_friction:.2f}")
    print("======================================================================\n")
    
    print("--- ALL TRADES ---")
    for _, r in trades.iterrows():
        print(f"{r['trade_id']} | {r['symbol']:<5} | {r['session_date']} | Entry: {r['entry_timestamp']} (${r['entry_price']:.2f}) -> Exit: {r['exit_timestamp']} (${r['exit_price']:.2f}) | Gross: ${r['gross_pnl']:+6.2f} | Net: ${r['net_pnl']:+6.2f} ({r['return_pct']:+5.2f}%) | Bars: {r['bars_held']:2d} | Horizon: {r['target_horizon_min']}m | Exit: {r['exit_reason']}")
        
    print("\n--- PERFORMANCE BY TARGET HORIZON ---")
    for h, grp in trades.groupby('target_horizon_min'):
        win_cnt = (grp['net_pnl'] > 0).sum()
        loss_cnt = (grp['net_pnl'] < 0).sum()
        gw = grp[grp['net_pnl'] > 0]['net_pnl'].sum()
        gl = abs(grp[grp['net_pnl'] < 0]['net_pnl'].sum())
        pf = gw / gl if gl > 0 else np.nan
        print(f"Horizon {h}m: N={len(grp)} | Net PnL: ${grp['net_pnl'].sum():+6.2f} | Mean Exp: ${grp['net_pnl'].mean():+5.2f} | Win Rate: {win_cnt/len(grp)*100:5.1f}% | PF: {pf:4.2f} | Avg Bars: {grp['bars_held'].mean():.1f} | Med Bars: {grp['bars_held'].median():.1f}")
        
    print("\n--- EXIT REASONS ---")
    for reason, grp in trades.groupby('exit_reason'):
        gw = grp[grp['net_pnl'] > 0]['net_pnl'].sum()
        gl = abs(grp[grp['net_pnl'] < 0]['net_pnl'].sum())
        pf = gw / gl if gl > 0 else np.nan
        print(f"{reason:<38} | N={len(grp):2d} | Net: ${grp['net_pnl'].sum():+6.2f} | Win%: {(grp['net_pnl']>0).mean()*100:5.1f}% | PF: {pf:4.2f}")
        
    print("\n--- SYMBOL CONTRIBUTIONS ---")
    syms = trades.groupby('symbol')['net_pnl'].agg(['count', 'sum', lambda x: (x > 0).mean()]).rename(columns={'<lambda_0>': 'win_rate'}).sort_values(by='sum', ascending=False)
    syms['contrib_pct'] = syms['sum'] / total_net * 100
    print(syms.to_string())
    
    print("\n--- SESSION CONTRIBUTIONS ---")
    days = trades.groupby('session_date')['net_pnl'].agg(['count', 'sum']).sort_values(by='sum', ascending=False)
    days['contrib_pct'] = days['sum'] / total_net * 100
    print(days.to_string())

if __name__ == "__main__":
    main()
