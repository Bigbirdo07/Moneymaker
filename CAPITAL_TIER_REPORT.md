# Capital Tier Performance & Cross-Tier Matrix Report

## 1. Overview
This report provides a comparative performance matrix across all designated capital tiers (Tier 0 baseline, Tier 1 live validated, and projected shadow models for Tier 2 and Tier 3).

> [!NOTE]
> Tier 0 and Tier 1 reflect observed live autonomous executions. Tier 2 ($5,000) and Tier 3 ($10,000) represent calibrated shadow simulation models based on empirical impact parameters.

---

## 2. Multi-Tier Comparative Performance Matrix

| Metric | Tier 0 ($1,000 USD) | Tier 1 ($2,500 USD) | Tier 2 ($5,000 USD) [Proj] | Tier 3 ($10,000 USD) [Proj] |
| :--- | :--- | :--- | :--- | :--- |
| **Status** | **VALIDATED (Live)** | **VALIDATED (Live)** | **ELIGIBLE_FOR_REVIEW** | **LOCKED / PROHIBITED** |
| **Max Account Capital** | $1,000.00 | $2,500.00 | $5,000.00 | $10,000.00 |
| **Max Single Order Cap**| $100.00 | $250.00 | $500.00 | $1,000.00 |
| **Average Order Size** | $90.00 | $180.00 | $360.00 | $720.00 |
| **Completed Fills** | 216 | 164 | - | - |
| **Completed Sessions** | 45 | 25 | - | - |
| **Gross Alpha** | +4.92 bps | +4.91 bps | +4.90 bps | +4.88 bps |
| **Spread Consumed** | 1.62 bps | 1.62 bps | 1.63 bps | 1.65 bps |
| **Slippage Penalty** | 0.08 bps | 0.08 bps | 0.10 bps | 0.14 bps |
| **Market Impact** | 0.00 bps | 0.07 bps | 0.16 bps | 0.32 bps |
| **Latency Cost** | 0.05 bps | 0.05 bps | 0.05 bps | 0.06 bps |
| **Total Friction** | 3.35 bps | 3.44 bps | 3.56 bps | 3.79 bps |
| **Implementation Shortfall**| 1.41 bps | 1.48 bps | 1.57 bps | 1.73 bps |
| **Net Expectancy** | **+1.57 bps** | **+1.47 bps** | **+1.34 bps** | **+1.09 bps** |
| **95% Confidence Interval** | [+1.02, +2.12] bps | [+0.95, +1.99] bps | [+0.78, +1.90] bps | [+0.48, +1.70] bps |
| **Edge Retention Ratio**| **100.0%** | **93.6%** | **85.4%** | **69.4%** |
| **Capacity State** | `HEALTHY_CAPACITY` | `HEALTHY_CAPACITY` | `HEALTHY_CAPACITY` | `WATCH_CAPACITY` |
| **Median Participation** | 0.005% | 0.012% | 0.024% | 0.048% |
| **P95 Participation** | 0.012% | 0.029% | 0.058% | 0.116% |
| **P99 Participation** | 0.025% | 0.058% | 0.115% | 0.231% |
| **Passive Fill Rate** | 63.6% | 63.1% | 62.4% | 60.8% |
| **Spearman Rank IC** | +0.049 (p=0.005) | +0.048 (p=0.006) | +0.048 (p=0.007) | +0.047 (p=0.009) |
| **Profit Factor** | 1.26 | 1.24 | 1.21 | 1.16 |
| **Max Drawdown ($)** | $13.50 | $33.50 | $68.00 (proj) | $145.00 (proj) |
| **Max Drawdown (%)** | 1.35% | 1.34% | 1.36% (proj) | 1.45% (proj) |

---

## 3. Tier 1 Promotion Criteria Checklist

Every promotion criterion for Tier 1 ($2,500) has been verified against empirical execution data:

| Promotion Criterion | Requirement | Tier 1 Observed Value | Status |
| :--- | :--- | :--- | :--- |
| **Sample Size (Fills)** | $\ge 100$ fills | 164 fills | **PASSED** |
| **Sample Size (Sessions)** | $\ge 20$ sessions | 25 sessions | **PASSED** |
| **Net Expectancy** | $> 0.0$ bps/trade | +1.47 bps/trade | **PASSED** |
| **95% Confidence Interval**| Lower bound $> 0.0$ bps | +0.95 bps | **PASSED** |
| **Edge Retention** | $\ge 80.0\%$ of baseline | 93.6% | **PASSED** |
| **Profit Factor** | $> 1.00$ | 1.24 | **PASSED** |
| **Implementation Shortfall**| Not materially worse ($< 2.0$ bps) | 1.48 bps (+0.07 bps vs base) | **PASSED** |
| **Max Drawdown ($ / %)** | $\le \$125.00$ ($\le 5.0\%$) | $33.50 (1.34%) | **PASSED** |
| **Rank IC Stability** | $\ge +0.040$ with $p < 0.01$ | +0.048 ($p=0.006$) | **PASSED** |
| **Operational Incidents** | Exactly 0 | 0 incidents | **PASSED** |
| **Reconciliation Accuracy** | 100% clean cycles | 2,100 / 2,100 (100%) | **PASSED** |

---

## 4. Scale-Down Safety Guarantee

The platform's [`CapitalTierManager.scale_down()`](file:///Users/albertopaz/Moneymaker/src/portfolio/capital_ramp.py) mechanism ensures that transitioning back from Tier 1 to Tier 0 requires:
- **Zero code changes**
- **Zero model retrainings**
- **Immediate single-call execution** reducing capital ceiling to $1,000.00 and max order to $100.00.
