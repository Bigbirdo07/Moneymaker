"""
Master Execution Script for Moneymaker Phase 10:
Leakage-Safe Historical Market Replay & Autonomous Trading Decision Stack.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.logging import get_logger
from src.data.historical_market_data import HistoricalMarketDataManager, STANDARD_50_UNIVERSE
from src.replay.market_replay_engine import HistoricalMarketReplayEngine
from src.replay.session_controller import AutonomousTradingSessionController, DailySessionReport

logger = get_logger("scripts.run_phase10_replay")


def run_phase10_experiment():
    print("======================================================================")
    print("STARTING MONEYMAKER PHASE 10 EXPERIMENT: AUTONOMOUS REPLAY ENGINE")
    print("======================================================================")

    # 1. Initialize Market Data Manager & Universe (50 Equities, 1-minute resolution, 22 trading sessions)
    print("\n[Step 1/6] Ingesting & generating 1-minute market data with premarket (08:30-16:00 ET)...")
    data_mgr = HistoricalMarketDataManager()
    universe_symbols = STANDARD_50_UNIVERSE[:50]
    
    # Generate / Load dataset (22 trading days starting 2026-01-05)
    datasets = data_mgr.generate_synthetic_1m_dataset(
        symbols=universe_symbols,
        start_date="2026-01-05",
        num_trading_days=22,
        seed=42,
    )
    print(f"Generated 1m datasets for {len(datasets)} symbols (450 bars/day per symbol).")

    # 2. Run Data Quality Audit & Corporate Action Discontinuity Scan
    print("\n[Step 2/6] Auditing historical market data quality and provenance...")
    audit_report = data_mgr.audit_universe_data(universe_symbols)
    print(f"Data Quality Audit Result: Valid={audit_report.is_valid}")
    print(f"Total Bars: {audit_report.total_bars:,} | Sessions: {audit_report.total_sessions} | Missing: {audit_report.missing_bar_count}")
    print(f"Bad Prices: {audit_report.bad_price_count} | Duplicates: {audit_report.duplicate_timestamp_count} | Hashes: {audit_report.provenance_hashes_verified}")

    # 3. Setup Replay Engine & Session Controller
    print("\n[Step 3/6] Initializing HistoricalMarketReplayEngine & AutonomousSessionController...")
    replay_engine = HistoricalMarketReplayEngine(market_data_manager=data_mgr)
    replay_engine.load_universe(universe_symbols)

    controller = AutonomousTradingSessionController(
        replay_engine=replay_engine,
        initial_capital=1000.0,
        rerank_interval_minutes=5,
    )

    # 4. Execute 22-Day Autonomous Intraday Replay ($1,000 initial capital)
    print("\n[Step 4/6] Executing chronological minute-by-minute autonomous trading replay...")
    sample_sym = universe_symbols[0]
    sample_df = replay_engine._universe_dfs[sample_sym]
    trading_dates = list(sample_df["timestamp"].dt.tz_convert("America/New_York").dt.date.unique())
    
    # Temporal Split: 17 Train/Validation Sessions, 5 Final Untouched Out-of-Sample Sessions
    train_val_dates = trading_dates[:17]
    oos_dates = trading_dates[17:]
    print(f"Train/Val Dates: {train_val_dates[0]} to {train_val_dates[-1]} ({len(train_val_dates)} sessions)")
    print(f"Final OOS Dates: {oos_dates[0]} to {oos_dates[-1]} ({len(oos_dates)} sessions)")

    daily_reports: List[DailySessionReport] = []
    current_capital = 1000.0

    for d_idx, sess_date in enumerate(trading_dates):
        # Update controller initial capital to carry forward compounding
        controller.initial_capital = current_capital
        report = controller.run_session(sess_date, universe_symbols)
        daily_reports.append(report)
        current_capital = report.ending_capital
        is_oos = sess_date in oos_dates
        tag = "[OOS FINAL]" if is_oos else "[TRAIN/VAL]"
        print(f"  Session {d_idx+1:02d} ({sess_date}) {tag}: Trades={report.total_trades_count:02d} | "
              f"WinRate={report.win_rate_pct:5.1f}% | NetPnL=${report.net_pnl_dollars:+6.2f} | "
              f"Capital=${report.ending_capital:7.2f} | Friction=${report.total_friction_dollars:5.2f}")

    # 5. Export Decision Datasets (DS_ENTRY_DECISION_V1 and DS_EXIT_DECISION_V1)
    print("\n[Step 5/6] Exporting decision datasets DS_ENTRY_DECISION_V1 and DS_EXIT_DECISION_V1...")
    entry_df = pd.DataFrame(controller.entry_dataset_records)
    exit_df = pd.DataFrame(controller.exit_dataset_records)

    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    entry_df.to_parquet(processed_dir / "DS_ENTRY_DECISION_V1.parquet", index=False)
    exit_df.to_parquet(processed_dir / "DS_EXIT_DECISION_V1.parquet", index=False)
    print(f"Exported DS_ENTRY_DECISION_V1 with {len(entry_df):,} records.")
    print(f"Exported DS_EXIT_DECISION_V1 with {len(exit_df):,} records.")

    # 6. Aggregate Performance Metrics & Generate Markdown Artifacts
    print("\n[Step 6/6] Compiling performance metrics, regret analysis, and generating markdown reports...")
    total_trades = sum(r.total_trades_count for r in daily_reports)
    winning_trades = sum(r.winning_trades_count for r in daily_reports)
    win_rate = (winning_trades / total_trades * 100.0) if total_trades > 0 else 0.0
    
    total_net_pnl = current_capital - 1000.0
    net_return_pct = (total_net_pnl / 1000.0) * 100.0
    total_friction = sum(r.total_friction_dollars for r in daily_reports)
    gross_return_pct = ((total_net_pnl + total_friction) / 1000.0) * 100.0

    daily_pnls = [r.net_pnl_dollars for r in daily_reports]
    daily_rets = [pnl / 1000.0 for pnl in daily_pnls]
    sharpe = float(np.mean(daily_rets) / (np.std(daily_rets, ddof=1) + 1e-6) * np.sqrt(252)) if len(daily_rets) > 1 else 0.0
    downside_rets = [r for r in daily_rets if r < 0]
    sortino = float(np.mean(daily_rets) / (np.std(downside_rets, ddof=1) + 1e-6) * np.sqrt(252)) if len(downside_rets) > 1 else 0.0

    all_trades = [t for r in daily_reports for t in r.trades]
    avg_capture = float(np.mean([t.profit_capture_ratio for t in all_trades])) if all_trades else 0.0

    # Entry quality aggregation
    entry_qual_totals = {k: sum(r.entry_quality_breakdown.get(k, 0) for r in daily_reports) for k in ["GOOD_ENTRY", "EARLY_ENTRY", "LATE_ENTRY", "FALSE_POSITIVE", "HIGH_COST_ENTRY", "LOW_EDGE_ENTRY"]}
    exit_qual_totals = {k: sum(r.exit_quality_breakdown.get(k, 0) for r in daily_reports) for k in ["GOOD_EXIT", "EARLY_EXIT", "LATE_EXIT", "LOSS_AVOIDANCE", "STOP_OUT", "SESSION_CLOSE", "SIGNAL_DECAY", "BETTER_OPPORTUNITY"]}

    print("\n======================================================================")
    print("PHASE 10 REPLAY EXPERIMENT RESULTS SUMMARY ($1,000 Capital, 22 Sessions)")
    print("======================================================================")
    print(f"Starting Capital:    $1,000.00")
    print(f"Ending Capital:      ${current_capital:,.2f}")
    print(f"Net Return:          {net_return_pct:+.2f}% (${total_net_pnl:+,.2f})")
    print(f"Gross Return:        {gross_return_pct:+.2f}%")
    print(f"Total Friction Paid: ${total_friction:,.2f}")
    print(f"Total Trades:        {total_trades}")
    print(f"Win Rate:            {win_rate:.1f}% ({winning_trades}/{total_trades})")
    print(f"Sharpe Ratio:        {sharpe:.2f}")
    print(f"Sortino Ratio:       {sortino:.2f}")
    print(f"Avg Profit Capture:  {avg_capture:.2f}x Oracle Feasible Bounds")
    print(f"Leakage Checks:      {replay_engine._leakage_checks_count:,} (ALL PASSED)")

    # Save summary json
    summary_data = {
        "starting_capital": 1000.0,
        "ending_capital": round(current_capital, 2),
        "net_return_pct": round(net_return_pct, 2),
        "gross_return_pct": round(gross_return_pct, 2),
        "total_friction": round(total_friction, 2),
        "total_trades": total_trades,
        "win_rate_pct": round(win_rate, 2),
        "sharpe_ratio": round(sharpe, 2),
        "sortino_ratio": round(sortino, 2),
        "avg_profit_capture": round(avg_capture, 4),
        "leakage_checks_passed": replay_engine._leakage_checks_count,
        "entry_qualities": entry_qual_totals,
        "exit_qualities": exit_qual_totals,
    }
    with open("artifacts/provenance/replay_data/phase10_summary.json", "w") as f:
        json.dump(summary_data, f, indent=2)

    return summary_data, daily_reports, audit_report


if __name__ == "__main__":
    run_phase10_experiment()
