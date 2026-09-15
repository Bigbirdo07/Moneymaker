# Alpha B Broker Paper Promotion Report (Phase 7A Track B)

**Strategy**: `ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL`  
**Execution Mode**: `ExecutionMode.ALPHA_B_BROKER_PAPER`  
**Deployable Candidate**: **Book B1 (Top-2 Long Only)**  
**Paper Capital**: **$10,000.00 USD (Virtual Research Paper)**  
**Sample Window**: 50 forward trading sessions across 10 liquid US equities  
**Evidence Type**: `BROKER_PAPER`

---

## 1. Executive Summary & Verdict

Alpha B was promoted from forward shadow to isolated broker paper under frozen configuration [`configs/frozen_alpha_b_paper_v1.yaml`](file:///Users/albertopaz/Moneymaker/configs/frozen_alpha_b_paper_v1.yaml).
- **Execution Mode**: `ALPHA_B_BROKER_PAPER` (Zero live capital access).
- **Book B1 (Long-Only Prototype)**: Validated as deployable candidate.
- **Book B2 (Long-Short Research Benchmark)**: Strictly non-deployable research only.
- **Track B Verdict**: **`ALPHA_B_PAPER_VALIDATED`** (Zero live capital authorized).

---

## 2. Broker Paper Performance (50 Sessions, 47 Completed 3-Day Cohorts)

| Metric | Book B1: Broker Paper (Top-2 Long) | Book B1: Conservative Shadow | Delta / Optimism | Unit |
| :--- | :--- | :--- | :--- | :--- |
| **Gross Cycle Return** | +16.4 | +16.2 | +0.20 | bps / 3D cycle |
| **Modeled Friction Drag**| 4.6 | 5.0 | -0.40 | bps / cycle |
| **Net Cycle Expectancy**| **+11.8** | **+11.2** | **+0.60** | bps / 3D cycle |
| **Annualized Net Return**| **+11.2%** | **+10.2%** | **+1.0%** | % / year |
| **Annualized Sharpe** | **0.92** | **0.88** | **+0.04** | Ratio |
| **Annualized Sortino** | **1.34** | **1.28** | **+0.06** | Ratio |
| **Maximum Drawdown** | **-4.4%** | **-4.8%** | **+0.4%** | % |
| **Daily Portfolio Turnover**| ~18.0% | ~18.0% | 0.0% | % / day |
| **Spearman Rank IC** | **+0.035** ($p=0.015$) | **+0.034** ($p=0.018$) | +0.001 | Rank Corr |
| **Paper Fill Advantage** | **+0.60** | 0.00 | **+0.60** | bps / cycle |

---

## 3. Cohort Accounting & Exposure State

The rolling 3-day holding period creates 3 overlapping cohorts of approximately \$3,333 USD each:
- **Max Active Cohorts**: 3 simultaneous cohorts.
- **Max Gross Exposure**: 100.0% (\$10,000 USD nominal virtual capital).
- **Max Single Symbol Exposure**: \$3,333.33 (33.3% during simultaneous 2-cohort selection) or \$2,500 capped per risk rules.
- **Double-Counting Prevention**: Capital is strictly partitioned per cohort date and tracked independently in the ledger.

---

## 4. Governance Verification

> [!IMPORTANT]
> - `ALPHA_B_BROKER_PAPER` is strictly sandboxed.
> - Any attempt to invoke `LIVE`, `LIVE_GOVERNED_MICRO`, or `LIVE_AUTONOMOUS_MICRO` with Alpha B triggers an immediate, uncatchable `AlphaBExecutionViolation`.
> - Short selling remains strictly prohibited in production.
