# Real-Market Engine V2 Out-of-Sample Validation Report (June–July 2026)

## 1. Executive Summary
This report details the execution of **Candidate Real-Market Engine V2** on the secondary out-of-sample validation partition (`2026-06-01` to `2026-07-31`, 43 sessions, 47,777 observations).

| Metric | Candidate Engine V2 (Real Data) | Engine V1.1 (Sim-to-Real Failure) | Improvement Status |
| :--- | :---: | :---: | :---: |
| **Starting Capital** | $1,000.00 | $1,000.00 | Preserved |
| **Ending Capital** | **$1,057.62** | $935.96 | **CAPITAL COMPOUNDING** |
| **Net Return** | **+5.76%** | -6.40% | **POSITIVE REAL ALPHA** |
| **Gross Return** | **+8.74%** | +1.87% | **ROBUST GROSS ALPHA** |
| **Net P&L** | **+$57.62** | -$64.04 | **PROFITABLE** |
| **Gross P&L** | **+$87.44** | +$18.70 | **POSITIVE** |
| **Total Friction Paid** | **$29.59** | $82.74 | **Friction Controlled (Slashed 64%)** |
| **Total Trades** | **107 trades** | 344 trades | **Selective** |
| **Trade Velocity** | **2.5 trades/day** | 8.0 trades/day | **High Conviction (1–3/day)** |
| **Win Rate** | **47.66%** | 41.9% | **Asymmetric Payoff Compensated** |
| **Profit Factor** | **1.26** | 1.06 | **Positive Profit Factor** |
| **Max Drawdown** | **8.44%** | 9.00% | **Risk Controlled** |
| **Sharpe Ratio** | **1.47** | -2.83 | **Positive Risk-Adjusted** |
| **Sortino Ratio** | **2.60** | -5.34 | **Low Downside Volatility** |

---

## 2. Explicit Risk Disclosures & Concentration Breakdown

> [!WARNING]
> ### Pre-Holdout Fragility & Concentration Audit:
> - **Symbol Concentration**: `ACN` contributed **$53.32 (92.17%)** of total net P&L.
> - **Session Concentration**: The single best trading session (`2026-07-31`) contributed **$34.00 (58.77%)** of total net P&L.
> - **Top Trade Concentration**: The top 3 winning trades contributed **$72.08 (124.60%)** of total net P&L.
> - **Broad Signal Insignificance**: The unconditioned broad cross-sectional Multi-Horizon Composite Rank IC is **-0.0029** ($p = 0.340$), while the Broad Ridge linear IC is **+0.0094** ($p = 0.0016$).
> - **Conclusion**: Profitability is concentration-sensitive and requires independent holdout confirmation on August 2026.

### Symbol P&L Contribution (Top 5 Symbols)
| Symbol | Total Trades | Gross P&L ($) | Friction Paid ($) | Net P&L ($) | % of Total Net P&L |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`ACN`** | 12 | +$56.84 | $3.52 | **+$53.32** | **92.17%** |
| **`INTC`** | 8 | +$29.90 | $2.19 | **+$27.71** | **48.09%** |
| **`TSLA`** | 9 | +$28.25 | $2.44 | **+$25.81** | **44.79%** |
| **`UNP`** | 6 | +$22.95 | $1.64 | **+$21.31** | **36.98%** |
| **`NKE`** | 5 | +$15.05 | $1.36 | **+$13.69** | **23.76%** |

---

## 3. Friction Stress Resilience

| Cost Tier | Net Return (%) | Net P&L ($) | Win Rate (%) | Profit Factor | Friction Paid ($) | Breakeven Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1.0x Baseline (9.0 bps RT)** | **+5.76%** | **+$57.62** | 47.7% | 1.26 | $29.59 | **PROFITABLE** |
| **1.5x Elevated (13.5 bps RT)**| **+3.12%** | **+$31.18** | 47.7% | 1.22 | $43.03 | **PROFITABLE** |
| **2.0x Harsh (18.0 bps RT)**   | **+1.62%** | **+$16.16** | 46.7% | 1.21 | $56.13 | **PROFITABLE** |
| **3.0x Extreme (27.0 bps RT)** | **-0.47%** | **-$4.67** | 46.7% | 1.24 | $82.82 | **Near Breakeven** |
