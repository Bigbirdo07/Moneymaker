# Turnover & Transaction Cost Attribution Report

## 1. Executive Summary

This report quantifies the drag exerted by transaction friction (bid-ask spread, slippage, and execution fees) on Autonomous Engine V1.0, and simulates strategy robustness under cost stress testing.

---

## 2. Friction Breakdown

Across the 658 round-trip trades executed during the 22-session test period:

| Friction Component | Baseline Rate / Model | Total Dollars Paid | Portfolio Drag (%) |
| :--- | :--- | :--- | :--- |
| **Half-Spread Entry & Exit** | Observed L1 Top of Book (~3.2 bps/leg) | $28.40 | 2.84% |
| **Microstructure Slippage** | Volume-Weighted Market Impact (~1.8 bps/leg) | $11.80 | 1.18% |
| **Exchange & Clearing Fees** | SEC / FINRA / Execution ($0.005/sh) | $2.80 | 0.28% |
| **Total Round-Trip Friction** | **~6.5 bps average per round-trip** | **$43.00** | **4.30%** |

```
P&L Bridge ($1,000 Starting Capital):
Gross P&L:             -$59.24  (-5.92%)
Transaction Friction:  -$43.00  (-4.30%)
----------------------------------------
Net Realized P&L:     -$102.24  (-10.22%)
```

---

## 3. Friction Stress Testing Across Cost Multipliers

To test strategy sensitivity to market illiquidity and widening spreads, the historical executions were re-evaluated across four cost scenarios:

| Scenario | Round-Trip Cost | Total Friction ($) | Net P&L ($) | Net Return (%) | Survival Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1.0x (Standard)** | 6.5 bps | $43.00 | -$102.24 | -10.22% | FAILED (Severe Drag) |
| **1.5x (Elevated Stress)** | 9.75 bps | $64.50 | -$123.74 | -12.37% | FAILED |
| **2.0x (High Stress)** | 13.0 bps | $86.00 | -$145.24 | -14.52% | FAILED |
| **3.0x (Extreme Stress)** | 19.5 bps | $129.00 | -$188.24 | -18.82% | CRITICAL FAILURE |

### Finding:
In Engine V1.0, every 1.0 bps increase in average round-trip friction costs the strategy ~$6.60 in equity (0.66% account drag) due to the 658-trade volume.

---

## 4. Projected Friction Under Engine V1.1

By reducing trade volume to ~88 trades per month via higher conviction gates and velocity caps:

| Strategy Engine | Trade Count | Avg Friction / Trade | Total Friction ($) | Capital Drag (%) |
| :--- | :---: | :---: | :---: | :---: |
| **V1.0 (Baseline)** | 658 | $0.0653 | $43.00 | 4.30% |
| **V1.1 (Calibrated)** | 88 | $0.0650 | $5.72 | 0.57% |
| **Net Savings** | **-570 trades (-86.6%)** | **—** | **+$37.28 saved** | **+3.73% saved** |
