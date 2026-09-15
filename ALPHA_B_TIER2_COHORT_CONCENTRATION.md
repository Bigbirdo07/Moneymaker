# Alpha B Tier 2 ($5,000 USD) Cohort Concentration & Overlap Report

## 1. Executive Summary
During the 60-session autonomous live evaluation of Alpha B at **$5,000 USD authorized capital** (B-Tier 2), a total of **52 3-day cohorts** were created and held through resolution. This report analyzes cohort overlap dynamics, concurrent active cohorts, same-symbol stacking, sector clustering, and portfolio capacity interactions under autonomous multi-day execution.

---

## 2. Cohort Concurrency & Capital Stacking

Alpha B trades a 3-day holding horizon with entries executed at market open ($T+0$) and mandatory exits at market open ($T+3$). At any given point during normal operations, up to 3 cohorts overlap concurrently.

| Metric | Observed Value | Limit / Threshold | Compliance Status |
| :--- | :--- | :--- | :--- |
| **Max Concurrent Cohorts** | 3 cohorts | 3 cohorts | PASS (Strict FIFO lifecycle) |
| **Mean Active Cohorts** | 2.68 cohorts | 3.00 max | PASS |
| **P50 Cohort Notional** | $1,590.00 USD | $2,500.00 max | PASS |
| **P95 Cohort Notional** | $1,940.00 USD | $2,500.00 max | PASS |
| **Peak Single Cohort Notional** | $2,120.00 USD | $2,500.00 max | PASS |
| **Peak Active Deployed Notional** | $4,480.00 USD | $5,000.00 cap | PASS ($89.60\%$ peak utilization) |

---

## 3. Same-Symbol Overlap & Re-Entry Friction

When an asset qualifies in consecutive cohorts, Alpha B's position limits prevent excessive concentration in a single instrument.

- **Total Position Entries Across 52 Cohorts**: 104 positions (2 per cohort target).
- **Same-Symbol Stacking Occurrences**: 4 instances where a symbol ranked in Top-2 in consecutive daily scans while an existing cohort held the symbol.
- **Handling Mechanism**: Sizing was dynamically clamped to the single-position ceiling ($1,250 USD per symbol across all cohorts).
- **Resized Orders**: 4 orders resized to preserve the single-symbol 25% portfolio cap ($1,250 USD).
- **Rejected Quantities**: Total rejected notional across all 4 events: $1,420.00 USD.
- **Missed Alpha Due to Symbol Cap**: Counterfactual evaluation of rejected quantities revealed $-1.20$ bps net return impact (rejecting excess concentration actually mitigated downside variance).

---

## 4. Sector & Beta Concentration

| Sector | Position Count | Share of Total Entries | Max Concurrent Weight | Sector Limit | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Technology** | 34 | 32.69% | $1,980.00 USD (39.6%) | 40.0% | PASS |
| **Financials** | 24 | 23.08% | $1,450.00 USD (29.0%) | 40.0% | PASS |
| **Consumer Discretionary** | 22 | 21.15% | $1,320.00 USD (26.4%) | 40.0% | PASS |
| **Health Care** | 14 | 13.46% | $920.00 USD (18.4%) | 40.0% | PASS |
| **Industrials / Energy** | 10 | 9.62% | $640.00 USD (12.8%) | 40.0% | PASS |

- **High-Beta Cluster Weight**: Peak combined weight in $\beta > 1.5$ stocks was **$2,100.00 USD (42.0%)**, safely within the 50.0% risk aggregator boundary.

---

## 5. Overnight Holding Concentration & Gap Exposure

All active Alpha B cohorts carry positions overnight between $T+0$ close and $T+3$ open.
- **Mean Overnight Gross Exposure**: $3,810.00 USD (76.2% of capital).
- **P95 Overnight Gross Exposure**: $4,410.00 USD (88.2% of capital).
- **Largest Single-Cohort Overnight Loss**: **-$38.40 USD (-0.77%)** during a macro gap-down on session #24.
- **Overnight Gap Filter Efficacy**: 2 scheduled cohort entries were deferred or aborted due to pre-market index gap exceedances ($> 1.50\%$), preventing an estimated $65.00 USD in slippage drag.

---

## 6. Summary Verdict

- **Cohort Concentration Risk**: **NOMINAL / CONTROLLED**
- **Symbol Stacking Rules**: **VERIFIED FUNCTIONAL**
- **Overnight Exposure Governance**: **HEALTHY**
