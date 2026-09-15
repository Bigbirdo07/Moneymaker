# Tier 3 ($10,000 USD) Pre-Registered Performance & Risk Forecast

> [!IMPORTANT]
> This forecast is pre-registered prior to any future authorized Tier 3 live session.
> Once human risk governance authorizes Tier 3, this forecast becomes immutable and will serve as the benchmark for evaluation.
> All metrics below are classified as `PROJECTED_MODEL`.

---

## 1. Governance & Capital Specification
- **Strategy ID**: `ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1`
- **Authorized Capital**: **$10,000.00 USD**
- **Single Order Cap**: **$1,000.00 USD** (10% sizing rule)
- **Loss Limits**:
  - Daily Loss Cap: **$200.00 USD (2.0%)**
  - Weekly Loss Cap: **$400.00 USD (4.0%)**
  - Pilot Drawdown Limit: **$500.00 USD (5.0%)**
- **Target Evaluation Sample**: $\ge 150$ fills across $\ge 25$ live sessions.

---

## 2. Pre-Registered Quantitative Expectations (`PROJECTED_MODEL`)

| Metric Dimension | Pre-Registered Tier 3 Target | 95% Confidence Interval | Baseline Reference (Tier 2 Observed) |
| :--- | :--- | :--- | :--- |
| **Gross Alpha** | **+4.88 bps** | [+3.90, +5.80] bps | +4.89 bps |
| **Total Round-Trip Friction** | **3.74 bps** | [3.45, 4.05] bps | 3.58 bps |
| **Net Expectancy** | **+1.14 bps** | **[+0.60, +1.68] bps** | +1.31 bps |
| **Absolute Edge Retention (vs Tier 0)**| **72.6%** | [38.2%, 107.0%] | 83.4% (`HEALTHY_CAPACITY`) |
| **Incremental Retention (vs Tier 2)**| **87.0%** | [45.8%, 128.2%] | 89.1% |
| **Capacity Classification State**| **`WATCH_CAPACITY`** | `WATCH_CAPACITY` (60–80%) | `HEALTHY_CAPACITY` |
| **Implementation Shortfall** | **1.74 bps** | [1.50, 2.05] bps | 1.58 bps |
| **Passive Fill Rate** | **60.5%** | [54.0%, 67.0%] | 62.6% |
| **Partial Fill Rate** | **4.8%** | [2.5%, 8.0%] | 2.1% |
| **P50 Dollar Participation** | **0.048%** | [0.030%, 0.070%] | 0.024% |
| **P95 Dollar Participation** | **0.116%** | [0.080%, 0.160%] | 0.058% |
| **P99 Dollar Participation** | **0.182%** | [0.120%, 0.250%] | 0.091% |
| **Max Expected Pilot Drawdown** | **$185.00 (1.85%)** | [$80.00, $320.00] | 1.25% ($62.50) |
| **Profit Factor** | **1.14** | [1.04, 1.25] | 1.19 |
| **Rank IC** | **+0.046** | [+0.015, +0.075] | +0.047 |

---

## 3. Cost-Stress Sensitivity Matrix for Tier 3

| Friction Multiplier | Effective Friction (bps) | Expected Net Alpha (bps) | Edge Retention % | Expected Status |
| :--- | :--- | :--- | :--- | :--- |
| **1.00x (Base Costs)** | 3.74 bps | **+1.14 bps** | 72.6% | `WATCH_CAPACITY` |
| **1.10x Costs** | 4.11 bps | **+0.77 bps** | 49.0% | `DEGRADED_CAPACITY` |
| **1.25x Costs** | 4.68 bps | **+0.20 bps** | 12.7% | `DEGRADED_CAPACITY` |
| **1.30x (Break-Even)** | 4.88 bps | **0.00 bps** | 0.0% | `CAPACITY_EXCEEDED` |
| **1.50x Costs** | 5.61 bps | **-0.73 bps** | -46.5% | `CAPACITY_EXCEEDED` |

* **Tier 3 Cost Break-Even Multiplier**: **$1.30\times$** (vs $1.37\times$ in Tier 2).
