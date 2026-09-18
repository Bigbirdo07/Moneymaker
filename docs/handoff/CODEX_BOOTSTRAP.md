# Moneymaker Quantitative Research Platform — Codex Bootstrap Guide

## 1. Mission

Moneymaker is intended to become:

> *"An autonomous, risk-first, intraday quantitative portfolio manager that starts with $1,000 as a proving ground, scans a broad dynamic universe of liquid U.S. equities, uses deterministic quantitative models to select/manage opportunities, uses MMRM as a senior quant research/risk/advisory interface, stays in cash when no opportunity qualifies, ends each day flat, learns only offline, and scales only if evidence supports it."*

---

## 2. Core Execution Constraints & Strategy Firewall

- **Asset Class**: Long-only U.S. Equities (listed, liquid, non-penny, non-leveraged).
- **Proving Environment**: Alpaca PAPER Trading.
- **Current Runtime**: Unity HPC Cluster (`/scratch3/workspace/.../MM`) via Slurm batch jobs.
- **Authorized Strategy Capital**: **`$1,000.00`** (`TIER_PAPER_1000`).
- **Capital Firewall**: Even if the broker paper account balance is larger (e.g. $100k paper equity), the deterministic strategy capital ledger strictly caps authorized equity at `$1,000`.
- **Intraday Flatten**: 100% Flat by 15:55 ET. Zero intentional overnight exposure.
- **Cash Decision**: CASH is a first-class valid decision. The system never forces trades.
- **Prohibited Instruments / Modes**:
  - `REAL_MONEY_NOT_AUTHORIZED` (hard runtime exception `RealMoneyAuthorizationError`).
  - No margin, leverage, short selling, options, or futures.

---

## 3. Control Hierarchy & MMRM Advisory Role

```
       Moneymaker Research Model (MMRM / LLM)
                         │
                         ▼ (Advisory / Research / Narrative Only)
         Deterministic Feature & Ranking Engine
                         │
                         ▼
        Deterministic SessionGate & Event Risk Engine
                         │
                         ▼
       Deterministic Sizing & Capacity (RiskPositionSizer)
                         │
                         ▼
             ExecutionAuthorization Firewall
                         │
                         ▼
            Alpaca PAPER Broker Adapter
```

- **MMRM Non-Execution Invariant**: MMRM operates strictly as a senior research analyst and advisory explainer.
- **Zero Direct Order Authority**: Language models cannot submit orders, alter risk sizing, override `SessionGate` (`NO_GO` / `CAUTION`), or bypass the real-money firewall.

---

## 4. Current Frozen Candidate & Policy

- **Candidate ID**: `PAPER_CANDIDATE_V1`
- **Policy ID**: `FORWARD_PAPER_POLICY_V1`
- **Policy SHA-256**: `9c2bc9f33a931f822fbd0574bbe28d7deefc87fb1da741604d3eec8207e0cb3b`
- **Freeze Manifest SHA-256**: `02813d0eae122293a1850bbaaa526b83ba83be19f419f7473bd546dbbf48d201`
- **Forward Block Target**: 20 qualifying true forward paper trading sessions.
- **Current Progress**: **`1 / 20 Sessions Complete`** (Completed session: `TRUE_FORWARD_20260918_PCV1_df3c84` on 2026-09-18).
- **Real Money Status**: `REAL_MONEY_NOT_AUTHORIZED`.

---

## 5. Frozen Policy Operating Rules (`FORWARD_PAPER_POLICY_V1`)

| Parameter | Value | Enforcement |
|---|---|---|
| **Market Open Cooldown** | 09:30:00 – 09:35:00 ET | Observe only; zero entries allowed |
| **Entry Window** | 09:35:00 – 14:30:00 ET | Entries evaluated minute-by-minute |
| **New Entry Cutoff** | 14:30:00 ET | Hard cutoff; zero new entries after 14:30 |
| **EOD Flatten Start** | 15:45:00 ET | Orderly position closure begins |
| **Target Flat** | 15:55:00 ET | Hard stop; portfolio must be 100% Cash |
| **Max Open Positions** | 1 position | Strictly single concurrent position |
| **Max Daily Entries** | 2 total entries / day | Maximum 1 entry per symbol per day |
| **Authorized Capital** | $1,000.00 | Strict strategy capital limit |
| **Normal Max Notional** | $750.00 | Max position notional in GO gate |
| **Normal Max Risk** | 0.75% ($7.50) | Risk budget per trade |
| **CAUTION Gate Rule** | 0.50x Risk ($3.75), 0.50x Notional ($375 ceiling), **30.0 bps** min net edge |
| **GO Gate Rule** | 1.00x Risk ($7.50), 1.00x Notional ($750 ceiling), **20.0 bps** min net edge |
| **NO_GO Gate Rule** | 0.0x Sizing, zero new entries allowed |
| **Macro Event Freeze** | [-15 min, +15 min] | High-impact events (CPI, FOMC, NFP, PPI, ISM) |
| **Daily Loss Limit** | 1.50% ($15.00) | Hard circuit breaker; halts new entries for session |

---

## 6. Current Development Philosophy

1. **The Core Architecture is Substantially Built**: All data pipelines, universe managers, feature models, sizing logic, paper adapters, reconciliation loops, and reporting systems exist and pass tests.
2. **Do Not Invent Unnecessary "Phases"**: The project is in active forward paper execution. The main constraint is accumulating genuine calendar time and unseen sessions, not writing endless feature layers.
3. **Preserve Strict Freeze**: Do not retune thresholds or swap models during the active 20-session block. Changes are permitted only for verified software, safety, or broker integration defects.
4. **Independent Code Grounding**: Read the repository files, inspect tests, verify hashes, and cross-check documentation against current HEAD before making any modifications.
