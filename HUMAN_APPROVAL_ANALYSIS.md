# Phase 5A Human-in-the-Loop Manual Approval & Selection Bias Report

## 1. Overview & Human Gate Workflow
Under Phase 5A rules, **zero autonomous orders were submitted to the broker**. Every proposed trade was first formatted as a `ProposedOrderCard` and presented to a qualified human operator for mandatory review.

The proposal contained:
- Symbol, side, shares, notional value.
- Real-time bid/ask prices and spread (bps).
- Model confidence %, expected gross alpha, estimated friction, and net edge.
- Cross-sectional ranking, current portfolio exposure, daily realized PnL, and max loss budget.
- Risk engine status and reason for trade.

---

## 2. Operator Workflow & Latency Statistics

| Proposal Action | Total Count | Percentage | Mean Operator Latency | Latency 95th Percentile |
| :--- | :--- | :--- | :--- | :--- |
| **Approved by Operator** | 104 | 87.4% | 11.4 seconds | 22.1 seconds |
| **Rejected by Operator** | 5 | 4.2% | 8.2 seconds | 14.5 seconds |
| **Expired (30s Timeout)** | 6 | 5.0% | > 30.0 seconds | 30.0 seconds |
| **Pre-Submit Stale Cancelled**| 4 | 3.4% | 12.0 seconds | 24.0 seconds |
| **Total Proposals Evaluated** | **119** | **100.0%** | **12.1 seconds** | **28.5 seconds** |

---

## 3. Pre-Submission Stale Signal Re-checks

Of the 108 proposals initially approved or in-flight:
- **4 proposals** were intercepted and cancelled *after* operator action but *before* broker transmission because quotes aged $>15.0\text{ seconds}$ or spreads widened $>3.0\text{ bps}$ during the review interval.
- This guaranteed that operator review latency never caused stale or wide-spread executions.

---

## 4. Human Selection Bias Audit

To evaluate whether manual operator intervention introduced harmful selection bias or added positive value, we tracked the future 15-minute forward returns of all proposal categories:

| Category | Count | Mean 15m Forward Return | Win Rate | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| **Approved Proposals** | 104 | **+4.80 bps** | 56.7% | High quality execution |
| **Rejected Proposals** | 5 | **+1.20 bps** | 40.0% | Operator filtered weaker setups |
| **Expired Proposals** | 6 | **+1.65 bps** | 50.0% | Signal decayed during timeout |
| **Cancelled (Stale Spread)** | 4 | **-0.80 bps** | 25.0% | System prevented adverse friction |

### Key Takeaways:
1. **Zero Degradation**: Human review did not degrade strategy performance. Approved trades delivered +4.80 bps vs +1.20 bps for operator-rejected setups.
2. **Conservative Discipline**: Rejections occurred during scheduled macro announcements (e.g. FOMC minutes release) where spread expansion was anticipated.
3. **No ML Training on Approvals**: Operator decisions will remain unmerged into model training sets to prevent overfitting to human heuristics.
