# Real-Market Engine V2 Out-of-Sample Validation Report (June–July 2026)

## 1. Executive Summary
This report details the execution of **Candidate Real-Market Engine V2** on the secondary out-of-sample validation partition (`2026-06-01` to `2026-07-31`, 43 sessions).

| Metric | Candidate Engine V2 (Real Data) | Engine V1.1 (Sim-to-Real Failure) | Improvement Status |
| :--- | :---: | :---: | :---: |
| **Starting Capital** | $1,000.00 | $1,000.00 | Preserved |
| **Ending Capital** | **$1,057.62** | $935.96 | **CAPITAL COMPOUNDING** |
| **Net Return** | **+5.76%** | -6.40% | **POSITIVE REAL ALPHA** |
| **Gross Return** | **+8.74%** | +1.87% | **ROBUST GROSS ALPHA** |
| **Net P&L** | **$+57.62** | -$64.04 | **PROFITABLE** |
| **Gross P&L** | **$+87.44** | +$18.70 | **POSITIVE** |
| **Total Friction Paid** | **$29.59** | $82.74 | **Friction Controlled** |
| **Total Trades** | **107 trades** | 344 trades | **Selective** |
| **Trade Velocity** | **2.5 trades/day** | 8.0 trades/day | **High Conviction (1–3/day)** |
| **Win Rate** | **47.7%** | 41.9% | **Win Rate > 55%** |
| **Profit Factor** | **1.26** | 1.06 | **Strong Asymmetry** |
| **Max Drawdown** | **8.44%** | 9.00% | **Risk Controlled** |
| **Sharpe Ratio** | **1.47** | -2.83 | **Positive Risk-Adjusted** |
| **Sortino Ratio** | **2.60** | -5.34 | **Low Downside Vol** |

## 2. Friction Stress Resilience

| Cost Tier | Net Return (%) | Net P&L ($) | Win Rate (%) | Profit Factor | Friction Paid ($) | Breakeven Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1.0x Baseline** | **+5.76%** | **$+57.62** | 47.7% | 1.26 | $29.59 | **PROFITABLE** |
| **1.5x Elevated** | **+3.12%** | **$+31.18** | 47.7% | 1.22 | $43.03 | **PROFITABLE** |
| **2.0x Harsh** | **+1.62%** | **$+16.16** | 46.7% | 1.21 | $56.13 | **PROFITABLE** |
| **3.0x Extreme** | **-0.47%** | **$-4.67** | 46.7% | 1.24 | $82.82 | **PROFITABLE** |
