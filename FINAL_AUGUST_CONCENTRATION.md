# Final August 2026 Holdout Concentration & Fragility Report

## 1. Overview & Governance Thresholds
Governance rules mandate explicit concentration auditing to determine whether profitability is driven by diversified edge or concentrated idiosyncratic outliers.

| Concentration Flag | Governance Threshold | Observed August Value | Flagged Status | Risk Assessment |
| :--- | :---: | :---: | :---: | :--- |
| `SINGLE_SYMBOL_CONCENTRATION` | > 30.0% of Net P&L | **68.77% (`ORCL`)** | **FLAGGED (TRUE)** | Severe single-stock dependency |
| `SINGLE_DAY_CONCENTRATION` | > 25.0% of Net P&L | **58.97% (`2026-08-19`)** | **FLAGGED (TRUE)** | Severe single-day dependency |
| `TOP3_TRADE_CONCENTRATION` | > 50.0% of Net P&L | **103.11% (Top 3 Trades)** | **FLAGGED (TRUE)** | Top 3 trades exceed 100% of net P&L |
| **Formal Concentration Verdict** | — | — | **`CONCENTRATION_SEVERE`** | Critical governance risk flag |

## 2. Symbol Contribution Breakdown

| Symbol | Trade Count | Win Rate (%) | Gross P&L ($) | Net P&L ($) | % of Total Net P&L | Cumulative % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ORCL** | 5 | 100.0% | +$37.34 | **+$35.50** | **+68.77%** | +68.77% |
| **ACN** | 2 | 100.0% | +$17.93 | **+$17.23** | **+33.39%** | +102.16% |
| **NFLX** | 1 | 100.0% | +$16.68 | **+$16.23** | **+31.44%** | +133.60% |
| **CMCSA** | 1 | 100.0% | +$15.68 | **+$15.21** | **+29.47%** | +163.07% |
| **NVDA** | 2 | 50.0% | +$14.70 | **+$13.87** | **+26.87%** | +189.94% |
| **AMD** | 1 | 100.0% | +$7.14 | **+$6.74** | **+13.05%** | +202.99% |
| **MCD** | 2 | 100.0% | +$5.98 | **+$5.13** | **+9.93%** | +212.92% |
| **NKE** | 2 | 50.0% | +$5.40 | **+$4.49** | **+8.71%** | +221.63% |
| **CSCO** | 1 | 100.0% | +$3.48 | **+$3.06** | **+5.92%** | +227.55% |
| **WMT** | 1 | 0.0% | -$0.76 | **-$0.97** | **-1.87%** | +225.68% |
| **ABT** | 1 | 0.0% | -$2.62 | **-$3.06** | **-5.92%** | +219.76% |
| **TSLA** | 1 | 0.0% | -$5.08 | **-$5.46** | **-10.57%** | +209.19% |
| **QCOM** | 1 | 0.0% | -$5.97 | **-$6.28** | **-12.17%** | +197.02% |
| **GOOGL** | 1 | 0.0% | -$6.18 | **-$6.63** | **-12.84%** | +184.18% |
| **LOW** | 1 | 0.0% | -$6.82 | **-$7.23** | **-14.00%** | +170.18% |
| **CRM** | 1 | 0.0% | -$8.10 | **-$8.49** | **-16.45%** | +153.73% |
| **INTC** | 4 | 25.0% | -$26.13 | **-$27.74** | **-53.74%** | **+100.00%** |
| **Total** | **28** | **57.1%** | **+$61.84** | **+$51.25** | **+100.00%** | — |

## 3. Session Contribution Breakdown

| Session Date | Trade Count | Session Net P&L ($) | % of Total Net P&L | Key Executed Trades |
| :---: | :---: | :---: | :---: | :--- |
| **2026-08-19** | 2 | **+$30.44** | **+58.97%** | ACN (+$14.21), NFLX (+$16.23) |
| **2026-08-27** | 1 | **+$21.40** | **+41.46%** | NVDA (+$21.40) |
| **2026-08-12** | 1 | **+$13.77** | **+26.68%** | ORCL (+$13.77) |
| **2026-08-13** | 1 | **+$11.18** | **+21.66%** | ORCL (+$11.18) |
| **2026-08-14** | 2 | **+$8.28** | **+16.04%** | CMCSA (+$15.21), INTC (-$6.94) |
| **2026-08-18** | 2 | **+$7.37** | **+14.28%** | NKE (+$13.65), QCOM (-$6.28) |
| **2026-08-28** | 2 | **+$6.15** | **+11.92%** | INTC (+$4.09), ORCL (+$2.06) |
| **2026-08-04** | 2 | **+$4.93** | **+9.55%** | AMD (+$6.74), TSLA (-$5.46) |
| **2026-08-21** | 1 | **+$3.03** | **+5.86%** | ACN (+$3.03) |
| **2026-08-06** | 2 | **+$0.11** | **+0.22%** | MCD (+$0.55), GOOGL (-$6.63) |
| **2026-08-05** | 2 | **-$0.88** | **-1.71%** | MCD (+$4.38), INTC (-$5.26) |
| **2026-08-07** | 2 | **-$1.37** | **-2.66%** | ORCL (+$4.10), INTC (-$5.47) |
| **2026-08-25** | 1 | **-$3.06** | **-5.92%** | ABT (-$3.06) |
| **2026-08-17** | 2 | **-$6.10** | **-11.82%** | CSCO (+$3.06), NKE (-$9.16) |
| **2026-08-26** | 1 | **-$7.23** | **-14.00%** | LOW (-$7.23) |
| **2026-08-20** | 2 | **-$9.46** | **-18.32%** | WMT (-$0.97), CRM (-$8.49) |
| **2026-08-10** | 2 | **-$26.94** | **-52.20%** | INTC (-$19.42), NVDA (-$7.53) |

## 4. Sector Concentration Breakdown

| Sector | Trade Count | Win Rate (%) | Net P&L ($) | % of Total Net P&L |
| :--- | :---: | :---: | :---: | :---: |
| **Technology** | 17 | 64.7% | **+$33.89** | **+65.65%** |
| **Communication Services** | 3 | 66.7% | **+$24.82** | **+48.08%** |
| **Consumer Defensive** | 1 | 0.0% | **-$0.97** | **-1.87%** |
| **Healthcare** | 1 | 0.0% | **-$3.06** | **-5.92%** |
| **Consumer Cyclical** | 6 | 50.0% | **-$3.06** | **-5.93%** |
| **Total** | **28** | **57.1%** | **+$51.25** | **+100.00%** |

## 5. Critical Concentration Assessment
- In June–July, `ACN` accounted for 92.17% of net P&L.
- In August, `ORCL` accounted for 68.77% of net P&L, `ACN` contributed another 33.39%, and the top 3 trades accounted for 103.11% of total net profits.
- While the candidate is profitable in both secondary validation (+5.76%) and final holdout (+5.12%), profitability remains heavily dependent on a handful of large multi-percent winners in the Technology/Communication sectors.
- This persistence of heavy concentration justifies the classification: **`CONCENTRATION_SEVERE`** and requires **`MORE_REAL_HISTORICAL_VALIDATION`** before paper trading can be scaled.
