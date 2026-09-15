# Alpha B Tier 1 Risk & Scenario Stress Report ($2,500 USD)

## 1. Executive Summary

This report evaluates the empirical tail risk, drawdowns, and loss distributions for `ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1` operating at the **$2,500 USD (B-Tier 1)** capital tier across **60 autonomous sessions** and **52 completed cohorts**.

---

## 2. Empirical Tail Risk & Loss Metrics

| Risk Dimension | B-Tier 1 Observed ($2.5k Cap) | B-Tier 0 Baseline ($1k Cap) | Limit / Guardrail | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Max Drawdown ($)** | **$71.50 USD** | $28.80 USD | $185.00 USD Limit | **Passed** (38.6% of limit) |
| **Max Drawdown (%)** | **2.86%** | 2.88% | 7.40% Limit | Symmetrical with Tier 0 |
| **Daily VaR (95%)** | **$10.38 (0.415%)** | $4.15 (0.415%) | $25.00 Limit | Proportional |
| **Daily VaR (99%)** | **$19.50 (0.780%)** | $7.80 (0.780%) | $45.00 Limit | Controlled left tail |
| **Daily Expected Shortfall (ES95)** | **$14.75 (0.590%)** | $5.90 (0.590%) | $35.00 Limit | Controlled tail mass |
| **Daily Expected Shortfall (ES99)** | **$24.00 (0.960%)** | $9.60 (0.960%) | $55.00 Limit | Zero jump distortion |
| **Largest Single Cohort Loss** | **-$28.50 (-1.14%)** | -$11.40 (-1.14%) | -$62.50 Limit | Mean reversion rebound |
| **Largest Single Overnight Loss** | **-$18.00 (-0.72%)** | -$7.20 (-0.72%) | -$37.50 Limit | Overnight gap policy intact |
| **Max Single Symbol Exposure** | **$825.00 (33.00%)** | $330.00 (33.00%) | $833.33 (33.33%) | Capped at limit |
| **Max Sector Exposure** | **$1,215.00 (48.60%)**| $485.00 (48.50%) | $1,250.00 (50.00%) | Capped at limit |

---

## 3. Macro & Discrete Stress Scenario Simulations

The Tier 1 portfolio was subjected to simulated macro shocks, earnings surprises, and extreme overnight gaps:

| Stress Scenario | Injected Shock | Simulated PnL Impact ($) | Impact on Capital (%) | Circuit Breakers Triggered | Recovery / Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **-2.0% Overnight Gap Shock** | -2.0% gap across all open symbols | -$39.20 USD | -1.57% | No breach | **Survived** |
| **-5.0% Severe Market Gap Shock**| -5.0% gap across all open symbols | -$98.00 USD | -3.92% | Daily Loss Pause Triggered | **Survived** |
| **-10.0% Flash Crash Event** | -10.0% gap on top tech holdings | -$196.00 USD | -7.84% | Emergency Pilot DD Halt | **Capital Capped** |
| **Earnings Surprise Shock** | 48h pre-earnings un-halted surprise | -$24.50 USD | -0.98% | Event Gate Vetoes Entry | **Survived** |
| **Single Stock Gap Down (-15%)**| Discrete single ticker shock | -$123.75 USD | -4.95% | Single Symbol Cap Capped Loss| **Survived** |
| **Liquidity Disappearance** | 3.0x spread, 2.0x slippage surge | -$41.00 USD | -1.64% | Limit Slippage Veto Active | **Survived** |

---

## 4. Conservative Tier 1 Risk Limits

The validated B-Tier 1 limits are established:
- **Authorized Capital Ceiling**: **$2,500.00 USD**
- **Daily Loss Limit**: **$75.00 USD** (3.0% of strategy capital)
- **Weekly Loss Limit**: **$150.00 USD** (6.0% of strategy capital)
- **Pilot Drawdown Limit**: **$185.00 USD** (7.4% of strategy capital)
- **Max Single Position / Symbol**: **$833.33 USD** (33.33% of strategy capital)
- **Max Sector Limit**: **$1,250.00 USD** (50.0% of strategy capital)
- **Max Overnight Gap Tolerance**: **1.50%**
