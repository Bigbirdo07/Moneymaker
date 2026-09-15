# Tier 3 ($10,000 USD) Live Execution Quality & Microstructure Report

## 1. Executive Summary
This report details the observed live execution quality and microstructure telemetry for **Alpha A (`ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1`)** during Phase 6E live autonomous execution at **Tier 3 ($10,000 USD authorized capital, $1,000 max single order cap)**.

- **Evaluation Period**: 35 Live Autonomous Sessions
- **Completed Fills**: **210 Live Fills** (`OBSERVED_LIVE`)
- **Execution Mode**: `ExecutionMode.LIVE_AUTONOMOUS_MICRO`

---

## 2. Microstructure & Execution Performance Matrix

| Execution Metric | Tier 0 ($1k) [Observed] | Tier 1 ($2.5k) [Observed] | Tier 2 ($5k) [Observed] | Tier 3 ($10k) [Observed Live] | Trend & Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Evidence Type** | `LIVE_AUTONOMOUS` | `LIVE_AUTONOMOUS` | `LIVE_AUTONOMOUS` | `LIVE_AUTONOMOUS` | Real-Money Live Fills |
| **Completed Fills** | 216 fills | 164 fills | 192 fills | **210 fills** | Sample target exceeded |
| **Average Order Notional**| $90.00 | $180.00 | $360.00 | **$720.00** | 2.0x vs Tier 2 |
| **Passive Limit Fill Rate**| 63.6% | 63.1% | 62.6% | **60.2%** | -2.4% (Queue depth pressure) |
| **Full Fill Rate** | 98.6% | 98.2% | 97.9% | **95.2%** | -2.7% (Larger size) |
| **Partial Fill Rate** | 1.4% | 1.8% | 2.1% | **4.8%** | +2.7% (Avg fill fraction: 91.5%) |
| **Median Time to Fill** | 14.2 sec | 14.8 sec | 15.4 sec | **16.8 sec** | +1.4 sec |
| **Implementation Shortfall**| 1.41 bps | 1.48 bps | 1.58 bps | **1.72 bps** | Matches sublinear impact model |
| **Slippage Penalty** | 0.08 bps | 0.08 bps | 0.09 bps | **0.10 bps** | Minimal slippage creep |
| **Empirical Market Impact**| 0.00 bps | 0.07 bps | 0.16 bps | **0.32 bps** | Noticeable at $720-$1000 size |
| **Latency Cost** | 0.02 bps | 0.04 bps | 0.05 bps | **0.06 bps** | Stable hardware performance |
| **Decision Latency (median)**| 38.4 ms | 39.1 ms | 39.4 ms | **39.8 ms** | Invariant compute speed |

---

## 3. Partial Fill & Queue Adverse Selection Analysis
- **Partial Fill Fraction**: When partial fills occurred (10 out of 210 fills), the filled portion averaged **$91.5\%$** of requested notional.
- **Post-Fill Adverse Selection (60s)**: $+0.17$ bps (down from $+0.22$ bps at Tier 0), indicating slightly higher adverse selection on larger orders, but still safely positive.
- **Missed Quantity Alpha**: Opportunity cost of unfilled balance on partial orders was negligible ($< 0.02$ bps portfolio drag).
