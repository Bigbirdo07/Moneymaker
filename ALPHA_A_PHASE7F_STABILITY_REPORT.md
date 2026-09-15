# Alpha A Phase 7F Stability & Capacity Hold Report

## 1. Executive Summary & Governance State

Under **Phase 7F**, `ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1` continued in its strictly governed **`PRODUCTION_CAPACITY_HOLD`** state at the frozen **$10,000 USD** capital ceiling under `LIVE_AUTONOMOUS_MICRO` execution.

Zero logic, parameter, universe, or risk model changes were made. All capital scaling beyond $10,000 USD remains strictly unauthorized.

---

## 2. Empirical Execution Economics & Capacity Metrics

Across 60 continuous live sessions observed in Phase 7F:

| Metric | Observed Tier 3 ($10k Cap) | Baseline Tier 2 ($5k Cap) | Baseline Tier 0 ($1k Cap) | Evaluation |
| :--- | :--- | :--- | :--- | :--- |
| **Gross Alpha** | **+4.870 bps / trade** | +4.920 bps / trade | +5.050 bps / trade | Highly consistent |
| **Canonical Friction** | **3.760 bps / trade** | 3.240 bps / trade | 2.450 bps / trade | Sublinear rise |
| **Net Expectancy** | **+1.110 bps / trade** | +1.680 bps / trade | +2.600 bps / trade | Statistically positive |
| **95% Confidence Interval** | **[+0.580, +1.640] bps**| [+1.120, +2.240] bps| [+1.850, +3.350] bps| Zero-bound excluded |
| **Absolute Edge Retention** | **70.70%** (vs Tier 2) | 64.62% (vs Tier 0) | 100.00% | `WATCH_CAPACITY` |
| **Cost Break-Even Multiplier**| **1.30x** | 1.52x | 2.06x | Narrow buffer |
| **Passive Fill Rate** | **89.40%** | 92.10% | 96.50% | Stable |
| **Mean Implementation Shortfall**| **1.76 bps** | 1.48 bps | 0.95 bps | Managed |
| **Realized Net Dollar PnL** | **+$666.00 USD** | +$504.00 USD | +$260.00 USD | Positive profit contribution |
| **Max Drawdown ($ / %)** | **$148.00 (1.48%)** | $78.00 (1.56%) | $18.50 (1.85%) | Controlled |

---

## 3. Capacity Diagnosis & Guardrails

1. **Watch Capacity Status**:
   Alpha A's net expectancy (+1.110 bps) and cost break-even multiplier (1.30x) confirm that while the strategy generates steady dollar profits at $10,000 USD, any further increase in order size would degrade fill quality and push execution friction past gross alpha.
2. **Capital Expansion Barrier**:
   Alpha A capital remains permanently capped at **$10,000 USD**. Success in Alpha B scaling or multi-strategy diversification provides zero justification for increasing Alpha A risk budgets.
3. **Formal Verdict**:
   $$\mathbf{CAPACITY\_HOLD\_WATCH}$$
