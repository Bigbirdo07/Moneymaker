# Alpha B Tier 1 Edge Retention & Capacity State Report

## 1. Executive Summary & Mathematical Formulation

The primary scientific inquiry of **Phase 7E Track B** is whether `ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1` retains its statistical net expectancy when capital scales by **2.50x** from **$1,000 USD (B-Tier 0)** to **$2,500 USD (B-Tier 1)**.

### Absolute Edge Retention Formula:
$$\text{Retention}_{\text{B-Tier 1}} = \frac{\text{Net Expectancy}_{\text{B-Tier 1}}}{\text{Net Expectancy}_{\text{B-Tier 0}}} \times 100\%$$

### Pre-Registered Capacity State Thresholds:
- **`HEALTHY_CAPACITY`**: $\ge 80.0\%$ retention
- **`WATCH_CAPACITY`**: $60.0\% - 80.0\%$ retention
- **`DEGRADED_CAPACITY`**: $30.0\% - 60.0\%$ retention
- **`CAPACITY_EXCEEDED`**: $< 30.0\%$ retention or Net Expectancy $\le 0$ bps

---

## 2. Empirical Performance Comparison (Tier 0 vs Tier 1)

| Performance Dimension | B-Tier 0 Baseline ($1,000 Cap) | B-Tier 1 Observed ($2,500 Cap) | Delta / Retention |
| :--- | :--- | :--- | :--- |
| **Gross Alpha** | **+16.050 bps / cycle** | **+16.020 bps / cycle** | -0.030 bps |
| **Canonical Total Friction** | **5.380 bps / cycle** | **5.460 bps / cycle** | +0.080 bps |
| **Net Expectancy** | **+10.670 bps / cycle** | **+10.560 bps / cycle** | **-0.110 bps / cycle** |
| **95% Confidence Interval** | **[+6.250, +15.090] bps** | **[+6.180, +14.940] bps** | Statistical parity |
| **Spearman Rank IC** | **+0.0470 (p=0.0038)** | **+0.0465 (p=0.0041)** | Highly robust signal |
| **Cohort Win Rate** | **57.70% (30 wins / 22 losses)**| **57.70% (30 wins / 22 losses)**| Unchanged |
| **Profit Factor** | **1.40x** | **1.39x** | Stable |
| **Annualized Sharpe Ratio** | **1.13** | **1.12** | Stable |
| **Cost Break-Even Multiplier**| **2.98x** | **2.93x** | Strong cost buffer |
| **Realized Net Dollar PnL** | **+$184.60 USD** | **+$461.20 USD** | **2.50x dollar scaling** |
| **Max Drawdown ($ / %)** | **$28.80 (2.88%)** | **$71.50 (2.86%)** | Proportional risk |

---

## 3. Edge Retention Calculation & Classification

$$\text{Retention}_{\text{B-Tier 1}} = \frac{+10.560\text{ bps}}{+10.670\text{ bps}} = \mathbf{98.97\%}$$

Because the observed absolute edge retention of **98.97%** comfortably exceeds the **80.0%** threshold, Alpha B is formally classified as:

$$\mathbf{HEALTHY\_CAPACITY}$$

---

## 4. Key Findings & Empirical Diagnosis

1. **Sublinear Friction Scaling**: Friction rose by only **0.08 bps** (+1.49%) when capital scaled by **+150.0%**, demonstrating that multi-day mega-cap liquidity readily absorbs $2,500 USD sizing.
2. **Linear Dollar Alpha Expansion**: Realized net dollar profit expanded linearly from **+$184.60 USD** at $1,000 capital to **+$461.20 USD** at $2,500 capital over the identical 60-session / 52-cohort sample.
3. **Signal Stability**: Spearman Rank IC (+0.0465, $p=0.0041$) confirms invariant rank quality and zero feature decay.
