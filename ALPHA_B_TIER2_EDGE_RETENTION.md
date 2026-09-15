# Alpha B Tier 2 Edge Retention & Capacity State Report

## 1. Executive Summary & Mathematical Formulation

The core scientific objective of **Phase 7F Track B** is to measure edge retention when `ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1` scales to **$5,000 USD (B-Tier 2)**.

### Mathematical Definitions:
$$\text{Tier 2 Absolute Retention} = \frac{\text{Net Expectancy}_{\text{B-Tier 2}}}{\text{Net Expectancy}_{\text{B-Tier 0}}} \times 100\%$$
$$\text{Tier 2 Incremental Retention} = \frac{\text{Net Expectancy}_{\text{B-Tier 2}}}{\text{Net Expectancy}_{\text{B-Tier 1}}} \times 100\%$$

### Pre-Registered Capacity Classifications:
- **`HEALTHY_CAPACITY`**: Absolute Retention $\ge 80.0\%$
- **`WATCH_CAPACITY`**: Absolute Retention $60.0\% - 80.0\%$
- **`DEGRADED_CAPACITY`**: Absolute Retention $30.0\% - 60.0\%$
- **`CAPACITY_EXCEEDED`**: Absolute Retention $< 30.0\%$ or Net Expectancy $\le 0$ bps

---

## 2. Three-Tier Empirical Performance Comparison

| Performance Dimension | B-Tier 0 ($1k Cap) | B-Tier 1 ($2.5k Cap) | B-Tier 2 ($5.0k Cap) | Cumulative Delta |
| :--- | :--- | :--- | :--- | :--- |
| **Gross Alpha** | **+16.050 bps** | **+16.020 bps** | **+15.980 bps** | -0.070 bps |
| **Canonical Friction** | **5.380 bps** | **5.460 bps** | **5.580 bps** | +0.200 bps |
| **Net Expectancy** | **+10.670 bps** | **+10.560 bps** | **+10.400 bps** | **-0.270 bps** |
| **95% Confidence Interval** | [+6.25, +15.09] bps | [+6.18, +14.94] bps | **[+6.05, +14.75] bps** | Statistical parity |
| **Spearman Rank IC** | +0.0470 (p=0.0038) | +0.0465 (p=0.0041) | **+0.0460 (p=0.0045)** | Signal intact |
| **Cohort Win Rate** | 57.70% | 57.70% | **57.70%** | Invariant |
| **Profit Factor** | 1.40x | 1.39x | **1.38x** | Stable |
| **Annualized Sharpe Ratio** | 1.13 | 1.12 | **1.10** | Stable |
| **Cost Break-Even Multiplier**| 2.98x | 2.93x | **2.86x** | Strong buffer |
| **Realized Net Dollar PnL** | +$184.60 USD | +$461.20 USD | **+$910.00 USD** | **4.93x dollar expansion** |
| **Max Drawdown ($ / %)** | $28.80 (2.88%) | $71.50 (2.86%) | **$142.50 (2.85%)** | Proportional |

---

## 3. Retention Calculations & Capacity State

$$\text{Absolute Retention} = \frac{+10.400\text{ bps}}{+10.670\text{ bps}} = \mathbf{97.47\%}$$
$$\text{Incremental Retention} = \frac{+10.400\text{ bps}}{+10.560\text{ bps}} = \mathbf{98.48\%}$$

Because absolute retention (**97.47%**) comfortably exceeds the **80.0%** threshold, Alpha B B-Tier 2 is formally classified as:

$$\mathbf{HEALTHY\_CAPACITY}$$

---

## 4. Formal Verdict

$$\mathbf{ALPHA\_B\_TIER2\_VALIDATED}$$
*(Alpha B successfully validates $5,000 USD capacity with 97.47% absolute edge retention, 2.86x cost break-even multiplier, and zero operational incidents).*
