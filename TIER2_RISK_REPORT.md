# Tier 2 Live Risk, Loss Budgets & Stress Testing Report

## 1. Executive Summary
During the 32 live sessions of Tier 2 evaluation at $5,000 capital, all percentage-denominated and dollar-denominated loss budgets were strictly maintained without a single breach.

---

## 2. Loss Budget Compliance Matrix

| Risk Parameter | Dollar Limit ($) | Percentage Limit (%) | Observed Max Live ($ / %) | Governance Status |
| :--- | :--- | :--- | :--- | :--- |
| **Daily Realized Loss Limit** | $100.00 | 2.0% | **$28.50 (0.57%)** | **CLEAN (Well below 2% limit)** |
| **Weekly Realized Loss Limit**| $200.00 | 4.0% | **$45.00 (0.90%)** | **CLEAN (Well below 4% limit)** |
| **Pilot Termination Drawdown** | $250.00 | 5.0% | **$62.50 (1.25%)** | **CLEAN (Max DD 1.25%)** |
| **Max Concurrent Positions** | 2 positions | 20.0% max notional ($1,000) | **2 positions ($980 max)** | **CLEAN** |

---

## 3. Empirical Value at Risk (VaR) & Expected Shortfall (ES)

Calculated via 10,000 block-bootstrap resamplings on observed Tier 2 live trade returns:

| Risk Metric | Dollar Amount ($) | Percentage of Equity (%) | Evidence Type |
| :--- | :--- | :--- | :--- |
| **1-Day VaR 95%** | **$28.50** | **0.57%** | `LIVE_AUTONOMOUS` |
| **1-Day VaR 99%** | **$49.80** | **1.00%** | `LIVE_AUTONOMOUS` |
| **1-Day ES 95%** | **$37.40** | **0.75%** | `LIVE_AUTONOMOUS` |
| **1-Day ES 99%** | **$61.20** | **1.22%** | `LIVE_AUTONOMOUS` |

---

## 4. Multi-Scenario Capacity Stress Testing

| Stress Scenario | Resulting Friction | Net Expectancy | Drawdown Impact | Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **1.25x Cost Multiplier** | 4.48 bps | **+0.41 bps** | Retains positive expectancy | **PASS** |
| **1.50x Cost Multiplier** | 5.37 bps | -0.48 bps | Unprofitable | **HALTED** |
| **Flash Crash (-5.0% Gap)**| - | - | -$50.00 loss (1.0% < 5.0% limit) | **PASS** |
| **Spread Shock (+3.0 bps)**| 6.58 bps | -1.69 bps | Orders rejected by gate | **PASS (Protected)**|
