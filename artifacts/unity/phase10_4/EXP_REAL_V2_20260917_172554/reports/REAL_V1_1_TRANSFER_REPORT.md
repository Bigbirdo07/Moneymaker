# Real Market Data Sim-to-Real Transfer Replay Report (Frozen V1.1)

## 1. Executive Summary & Verification
This report details the execution of **Frozen Autonomous Engine V1.1** on **REAL historical 1-minute market data from Alpaca/IEX** across 43 trading sessions (`2026-03-01` to `2026-04-30`). Zero parameters were tuned, and zero retraining was performed.

| Metric | Frozen V1.1 Real Performance | Calibrated Simulation Benchmark | Empirical Transfer Verdict |
| :--- | :---: | :---: | :---: |
| **Starting Capital** | $1,000.00 | $1,000.00 | Preserved |
| **Ending Capital** | **$935.96** | $1,052.70 | Capital Preserved 93.6% |
| **Net Return** | **-6.40%** | +5.27% | **FRICTION DEFICIT** |
| **Gross Return** | **+1.87%** | +7.80% | **GROSS ALPHA POSITIVE** |
| **Net P&L** | **-$64.04** | +$52.70 | Deficit |
| **Gross P&L** | **+$18.70** | +$78.00 | Positive |
| **Total Friction Paid** | **$82.74** | $25.30 | Friction Drag ($82.74 > $18.70) |
| **Total Trades** | **344 trades** | 88 trades | Hit 8/day cap |
| **Trade Velocity** | **8.0 trades/day** | 4.0 trades/day | Max Allowed Velocity |
| **Win Rate** | **41.9%** | 55.8% | Below 50% Threshold |
| **Profit Factor** | **1.06 (Gross)** | 1.85 (Net) | Marginal Gross Edge |
| **Max Drawdown** | **9.00%** | 3.65% | Moderate Drawdown |
| **Sharpe Ratio (Annualized)** | **-2.83** | +2.15 | Net Negative |
| **Sortino Ratio** | **-5.34** | +3.40 | Net Negative |

---

## 2. Replay Configuration & Constraints
- **Data Source**: Alpaca Historical Bars API (`ALPACA_IEX` feed, real recorded trades)
- **Evidence Class**: `SIMULATED_EXECUTION_ON_REAL_MARKET_DATA`
- **Capital Allocation**: Whole shares only, max 33% capital per position, max 3 concurrent positions
- **Execution Latency**: 1-bar execution delay ($T+1$ next-minute open)
- **Trading Sessions**: 43 sessions across March and April 2026

---

## 3. Key Scientific Findings
1. **Gross Directional Edge is Positive (+1.87%, +$18.70)**: The engine's raw predictive logic generated more gross dollar gains than gross dollar losses on real market data (Gross Profit Factor = 1.06).
2. **Gross Edge Does Not Exceed Real Microstructure Friction**: In simulation, Decile 10 produced +26.8 bps gross. On real IEX market data, Decile 10 produced only +0.64 bps gross over 15 minutes, which is insufficient to overcome the 6.5 bps round-trip friction.
3. **Friction Drag Overcomes Capital**: Over 344 trades, total friction paid was **$82.74**, converting a **+$18.70 gross gain** into a **-$64.04 net loss**.
4. **Velocity Reached the 8 Trades/Day Cap**: Because threshold gates calibrated on synthetic data triggered too frequently on real leptokurtic price paths, trade velocity ran at the maximum allowed ceiling (8.0 trades/day).
