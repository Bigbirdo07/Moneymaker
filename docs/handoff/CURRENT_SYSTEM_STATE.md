# CURRENT SYSTEM STATE — MONEYMAKER

**Snapshot Timestamp**: `2026-09-18T13:50:00-04:00`  
**Git Branch**: `main`  
**Git Commit SHA**: `2f46360` (or current HEAD)  
**Working Tree State**: Clean / fully synchronized with `origin/main`  
**Test Suite Status**: **`455 passed, 0 failed`** (`pytest -q`)

---

## 1. Governance & Candidate Specification

| Field | Value |
|---|---|
| **Candidate ID** | `PAPER_CANDIDATE_V1` |
| **Policy ID** | `FORWARD_PAPER_POLICY_V1` |
| **Policy Hash (SHA-256)** | `9c2bc9f33a931f822fbd0574bbe28d7deefc87fb1da741604d3eec8207e0cb3b` |
| **Freeze Manifest Hash** | `02813d0eae122293a1850bbaaa526b83ba83be19f419f7473bd546dbbf48d201` |
| **Strategy Capital Tier** | `TIER_PAPER_1000` ($1,000.00 authorized strategy equity) |
| **Execution Environment** | `PAPER` (Alpaca Paper API) |
| **Active Runtime Host** | Unity HPC Cluster (`/scratch3/workspace/.../MM`) |
| **Universe Mode** | Phase B Dynamic Universe (Screening -> Liquidity -> DataQuality -> FastScanner -> Ranking) |
| **Real Money Trading** | **`REAL_MONEY_NOT_AUTHORIZED`** |

---

## 2. Active Forward Block Progress

- **Target Block Duration**: 20 qualifying true forward paper trading sessions.
- **Current Progress**: **`1 / 20 Sessions Complete`** (5.0%).
- **Current Validation State**: `FORWARD_PAPER_EVIDENCE_ACCUMULATING`.
- **Latest Qualifying Session**:
  - **Session ID**: `TRUE_FORWARD_20260918_PCV1_df3c84`
  - **Market Date**: `2026-09-18`
  - **Slurm Job ID**: `64571170`
  - **Compute Node**: `uri-cpu032`
  - **Session Gate**: `CAUTION`
  - **Trades Executed**: `0` (15 top candidates screened; none cleared 30 bps net hurdle under CAUTION gate)
  - **EOD Portfolio State**: `100% FLAT (CASH)`
  - **Reconciliation**: `CLEAN`
  - **Verdict**: `TRUE_FORWARD_PAPER_SESSION_COMPLETED_CASH`
  - **Counts Toward Block**: **`TRUE`**

---

## 3. Primary Research Question

> **Current Research Question**:  
> *"Does `PAPER_CANDIDATE_V1` produce positive and sufficiently diversified net expectancy across genuinely unseen forward sessions?"*

*(Note: We no longer ask whether the system can trade; historical blind simulation proves it makes selective entries when high net edge is present).*

---

## 4. Empirical Diagnostic Findings

### A. Historical Missed-Opportunity & Rejection Pool Audit
- **Evidence Class**: `POST_HOC_HISTORICAL_DIAGNOSTIC`
- **Rejection Sample**: 383 rejected candidate opportunities evaluated counterfactually across historical data.
- **Breakdown**:
  - `141` Profitable setups after costs (**36.8%**)
  - `162` Unprofitable / stopped setups (**42.3%**)
  - `80` Breakeven / insufficient movement (**20.9%**)
- **Economic Balance**:
  - Estimated missed profits: **`~$324.00`**
  - Estimated avoided losses: **`~$413.34`**
  - **Net Economic Protection Benefit**: **`+$89.34`**
  - Rejected-Pool Profit Factor: **`0.77`**
- **Takeaway**: The filtered rejection pool as a whole had negative expectancy (< 1.0 PF). The hurdle filters bad trades more than it forfeits good ones.

---

### B. Blind Historical Week Simulation (May 2026)
- **Evidence Class**: `BLIND_HISTORICAL_WALK_FORWARD_DIAGNOSTIC` (`COUNTS_TOWARD_FORWARD_BLOCK = FALSE`)
- **Deterministic Selection**: Mechanically chosen month `2026-05` (Seed: `20260918`) across 31 eligible complete months without prior inspection of profitability.
- **Knowledge Boundary**: Model training strictly ended `2026-04-30` (`training_end_date < test_start_date`).
- **Sessions Tested**: `2026-05-01`, `2026-05-04`, `2026-05-05`, `2026-05-06`, `2026-05-07`.
- **Primary Frozen Book (`BOOK_FROZEN_30`)**:
  - Starting Equity: `$1,000.00` | Ending Equity: **`$998.02`** (Net P&L: **`-$1.98`** / -0.20%)
  - Trades: `4` | Cash Days: `1` | Win Rate: `25.0%` (1W / 3L) | Profit Factor: `0.76`
  - Trade Details:
    1. `2026-05-01`: **INTC** -> **`+$5.75`** net (Target Met)
    2. `2026-05-04`: **PM** -> **`-$1.07`** net (EOD Flatten)
    3. `2026-05-05`: **INTC** -> **`-$3.25`** net (Stopped Out)
    4. `2026-05-06`: **CASH** -> **`$0.00`** (Best rejected setup: MRK -> would have lost `-$0.84`; gate saved capital)
    5. `2026-05-07`: **INTC** -> **`-$3.40`** net (Stopped Out)
  - Avg Capital Deployed: `$160.23` | Max Capital Deployed: `$223.90`

### C. Shadow Gate Comparisons (Research Only)
- **`BOOK_SHADOW_25` (25 bps hurdle)**: 5 trades, Ending Equity `$997.18` (Net `-$2.82`), PF `0.69`.
- **`BOOK_SHADOW_20` (20 bps hurdle)**: 5 trades, Ending Equity `$999.05` (Net `-$0.95`), PF `0.90`.
- **Conclusion**: Lowering the gate generated higher turnover without establishing positive expectancy. `BOOK_FROZEN_30` remains frozen.

---

## 5. Concentration Watchlist

- In the 5-day blind simulation, **INTC** accounted for **3 of 4 trades (75%)**.
- While INTC produced the largest winning trade (+$5.75), concentration risk is a primary structural vulnerability observed in prior historical holdouts (e.g., ORCL in August 2026 holdout, TSLA in 2023 holdout).
- Forward metrics must continuously track:
  - Single-symbol trade contribution (Top-1 / Top-3 P&L contribution).
  - Sector concentration vs. universe breadth.
