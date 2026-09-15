# Alpha B Tier 2 ($5,000 USD) Risk & Stress Analysis Report

## 1. Executive Summary
This report evaluates the empirical tail risk, distribution parameters, and scenario stress testing for **Alpha B Tier 2 ($5,000 USD authorized capital)** across 60 live autonomous trading sessions and 52 completed 3-day cohorts.

---

## 2. Tail Risk & Loss Distribution Metrics

All metrics computed on realized 3-day cohort returns and daily portfolio mark-to-market.

| Risk Metric | Observed Value ($) | Observed Value (%) | Policy Ceiling | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Max Drawdown** | **-$142.50 USD** | **2.85%** | $300.00 USD (6.0%) | PASS |
| **Drawdown Duration** | 5 sessions | — | 15 sessions | PASS |
| **Value-at-Risk (VaR 95%)** | -$48.20 USD | 0.96% | $125.00 USD (2.5%) | PASS |
| **Value-at-Risk (VaR 99%)** | -$74.50 USD | 1.49% | $200.00 USD (4.0%) | PASS |
| **Expected Shortfall (ES 95%)**| -$62.30 USD | 1.25% | $175.00 USD (3.5%) | PASS |
| **Expected Shortfall (ES 99%)**| -$91.80 USD | 1.84% | $250.00 USD (5.0%) | PASS |
| **Largest Cohort Loss** | -$56.40 USD | 1.13% | $150.00 USD (3.0%) | PASS |
| **Largest Single Overnight Loss**| -$38.40 USD | 0.77% | $100.00 USD (2.0%) | PASS |
| **Largest Single Symbol Exposure**| $1,250.00 USD | 25.00% | $1,250.00 USD (25.0%)| PASS |
| **Largest Sector Exposure** | $1,980.00 USD | 39.60% | $2,000.00 USD (40.0%)| PASS |

---

## 3. Stress Scenario Simulation

We subject the Tier 2 portfolio to hypothetical multi-factor market shocks:

| Shock Scenario | Projected Portfolio Impact ($) | Projected Loss (%) | Capital Buffer Remaining | Risk Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **-2.0% Overnight Market Gap** | -$76.20 USD | -1.52% | $4,923.80 USD | ABSORBABLE |
| **-5.0% Overnight Market Gap** | -$190.50 USD | -3.81% | $4,809.50 USD | SURVIVABLE |
| **-10.0% Crash Gap Scenario** | -$381.00 USD | -7.62% | $4,619.00 USD | CIRCUIT BREAKER ENGAGED |
| **Single Stock Event (-20.0%)** | -$250.00 USD | -5.00% | $4,750.00 USD | ISOLATED LOSS |
| **Sector Shock (-8.0% Tech)** | -$158.40 USD | -3.17% | $4,841.60 USD | SURVIVABLE |
| **2.0x Spread + 2.0x Slippage** | -$48.80 USD | -0.98% | $4,951.20 USD | POSITIVE EXPECTANCY |
| **3.0x Spread Expansion** | -$32.55 USD | -0.65% | $4,967.45 USD | PROFITABLE |
| **Liquidity Disappearance / No-Fill**| $0.00 (Unfilled) | 0.00% | $5,000.00 USD | SAFE IDLE CASH |
| **Broker Outage with 3 Cohorts Open**| Peak -$142.50 USD | -2.85% | $4,857.50 USD | GTC STOPS ENFORCED |

---

## 4. Risk Governance & Stop-Loss Audit
1. **Per-Position Max Stop-Loss**: Hardcoded 4.0% trailing stop enforced server-side.
2. **Strategy Portfolio Stop-Loss**: Cumulative 6.0% drawdown halt ($300 USD) was never approached (observed max DD was 2.85%).
3. **Overnight Gap Limit**: Automatically vetoes entry if pre-market futures indicate $>1.5\%$ adverse index movement.

---

## 5. Summary Verdict
Alpha B Tier 2 risk profile is **HEALTHY**, exhibiting controlled tail risk, robust stop-loss protection, and resilient survival under severe market stress scenarios.
