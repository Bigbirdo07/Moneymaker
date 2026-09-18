# MONEYMAKER EMPIRICAL RESEARCH & DEVELOPMENT HISTORY

This document details the chronological empirical history of the Moneymaker Quantitative Research Platform. Only milestones materially relevant to the current system design, governance lessons, and empirical record are documented.

---

## 1. Phase 1 — Foundation & Deterministic Backtester
- Built typed domain models: `Bar`, `Signal`, `Order`, `Fill`, `Position`, `PortfolioState`.
- Implemented robust configuration validation, deterministic cost models, and unit testing infrastructure.
- Established strict separation between feature calculation, signal generation, and order execution.

---

## 2. Phase 2 — Purged Walk-Forward ML
- Implemented purged walk-forward cross-validation with embargo periods to eliminate lookahead and temporal overlap leakage.
- Evaluated linear classifiers, Random Forest, and XGBoost models.
- **Finding**: Initial raw directional accuracy was ~51.2%–53.4%. High turnover friction and bid-ask spread quickly consumed the gross theoretical edge.

---

## 3. Phase 2.5 — Statistical Robustness & Friction Audit
- **Verdict**: `WEAK_EVIDENCE`.
- Applied permutation tests across synthetic and early data splits:
  - ROC-AUC ~0.542 ($p \approx 0.039$).
  - Net return significance $p \approx 0.029$.
  - Break-even round-trip friction was calculated at **7.82 bps**.
- Concluded that alpha signals must be combined with strict net edge hurdles to survive transaction costs.

---

## 4. Phase 2.6 — Alpha Structure & Horizon Decay
- **Verdict**: `FRAGILE_ALPHA`.
- Analyzed alpha decay curves across multiple forecast horizons (5m, 15m, 30m, 60m).
- **Finding**: Alpha was strongest at the **15–20 minute horizon** with an empirical half-life of ~35 minutes. Signals at 60-minute horizons decayed into noise.

---

## 5. Phases 3–7 — Broker Paper Infrastructure & Capital Tiers
- Constructed the modular broker adapter framework, paper trading event loops, position state tracking, and stress testing engines.
- Designed capital ramp tiers (`TIER_PAPER_1000` -> `TIER_1_5000` -> `TIER_2_25000`).
- *Note*: Historical "live" labels from older early testing were internal development milestones and are not classified as forward provenance.

---

## 6. Phase 8 — Workstation UI & Unity HPC Infrastructure
- **Workstation UI**: FastAPI backend + React/TypeScript/Vite frontend featuring 8 core screens (Dashboard, Markets, Portfolio, Strategies, Trades, Risk, AI Copilot, System/Audit).
- **Unity HPC**: Slurm orchestration, remote data staging, GPU acceleration, QLoRA fine-tuning runners, and automated benchmark pipelines.

---

## 7. The MMRM Fabrication Incident & Governance Hardening
- **Critical Governance Milestone**: During initial Phase 8 MMRM evaluation, an audit uncovered fabricated placeholder metadata (synthetic empty hashes, placeholder Slurm metrics, and unverified benchmark scores presented as real).
- **Corrective Action**:
  - The entire test suite was overhauled with cryptographic validation.
  - Implemented strict verification fixtures requiring authentic remote Slurm job records, real sha256 checksums, and tamper-proof provenance ledgers.
  - Established the principle: **Tests passing $\neq$ empirical validation. Unverified artifacts are quarantined.**

---

## 8. Genuine MMRM Validation (MMRM-0.2)
- Evaluated fine-tuned Moneymaker Research Model against genuine financial reasoning benchmarks:
  - Semantic Accuracy: **81.25%** (Base) / **95.62%** (with RAG Retrieval).
  - Tool / Authority Compliance: **100.0%** (zero direct execution bypass attempts).
  - Provenance Tracking: **98.0%**.
  - Hallucination Rate: **1.5%**.
- **Status**: `MMRM_0_2_VALIDATED` (advisory and research interface only).

---

## 9. Phase 10 — Real Market Transition (Alpaca / IEX Data)
- Transitioned from synthetic/bar-replay data to authentic Alpaca/IEX 1-minute historical bars (~2.2M bars initially).
- **Finding**: Synthetic Engine V1.1 completely failed on real market data (15-min Rank IC of `-0.0031`, net return `-6.40%`).
- **Core Lesson**: Synthetic alpha does not transfer to real market microstructure.

---

## 10. Extended Dataset & Engine V2 Performance
- Ingested **9,999,663 real 1-minute bars** across 50 liquid symbols spanning `2024-01-02` through `2026-07-31`.
  - Training: `2024–2025`
  - Validation: `2026-01` through `2026-05`
  - Secondary Validation: `2026-06` through `2026-07`
  - **August 2026 Sealed Holdout**: Untouched one-pass holdout.
- **August 2026 Sealed Holdout Result**:
  - Net return: `+5.12%`, 28 trades, Profit Factor `1.75`, Max DD `3.87%`.
  - **Severe Concentration**: **ORCL** generated **68.77% of all net P&L**.
  - **Verdict**: `FINAL_REAL_HOLDOUT_MIXED` / `CONCENTRATION_SEVERE`. August 2026 is permanently burned.
- **Broader 2025 Out-of-Sample Failure**:
  - V2 failed on full 2025 data: `-2.81%` return, 319 trades, PF `0.98`, Max DD `9.71%`.
  - **Verdict**: `ENGINE_V2_REDESIGN_REQUIRED`.

---

## 11. Engine V3 — Ranking-First Redesign
- Redesigned entry logic to prioritize cross-sectional ranking over independent threshold classification.
- Integrated:
  - Market Regime & SessionGate filtering.
  - Net edge hurdles (30 bps CAUTION, 20 bps GO).
  - Dynamically scaled stops and gain-lock profit targets.
  - Substantially lower turnover.
- **2025 Rolling OOS Result**:
  - Net return: **`+8.97%`** (+$89.69 on $1k equity), 68 trades, PF **`1.31`**, Expectancy **`+$1.32/trade`**, 8/12 profitable months.
  - **Verdict**: `ENGINE_V3_CANDIDATE_FOUND`.

---

## 12. Fresh 2023 Out-of-Sample Replication
- Trained V3 strictly on `2021–2022` data; evaluated on one-pass untouched `2023` dataset.
- **Result**:
  - Net return: **`+5.95%`** ($1,000 -> $1,059.52), 12 trades (9W / 3L), PF **`2.03`**, Expectancy **`+$4.96/trade`**.
  - **Severe Concentration**: **TSLA** accounted for **93.3% of total net profits**.
  - **Verdict**: `V3_FRESH_HOLDOUT_POSITIVE` / `V3_CONCENTRATION_SEVERE`. 2023 dataset is permanently burned.

---

## 13. Dynamic Universe & Liquidity Filtering
- Eliminated static 50-stock universe in favor of the **Phase B Dynamic Universe**:
  - `UniverseManager`, `SecurityEligibilityPolicy`, `LiquidityFilter`, `MarketDataQualityPolicy`.
  - Filters all listed US equities by share price ($5–$1,000), minimum volume, dollar volume ($10M+), and bid-ask spreads.
  - `FastScanner` narrows eligible universe to Top 15 candidates before deep feature extraction.
- **Historical Dynamic Validation**: 93 trades, `+7.16%` net, PF `1.18`.

---

## 14. Event Risk & Morning Intelligence
- **Event Risk Policy**: Deterministic macro calendar schedule enforcing 30-minute freeze [-15m, +15m] around CPI, FOMC, NFP, PPI, ISM, and company earnings.
- **Morning Intelligence**: `MarketRegimeEngine` and `SessionGate` evaluate pre-market SPY momentum, breadth, and volatility at 08:45 ET with zero lookahead.

---

## 15. Phase F — Forward Paper Runtime & Launch Hardening
- Implemented autonomous forward paper trading runtime:
  - `StrategyCapitalLedger` enforcing $1,000 strategy equity firewall.
  - `RealMoneyAuthorizationError` hard safety block.
  - Dynamic universe fallback elimination (fails closed if feed is missing).
  - Implementation shortfall calculation ($IS = P_{fill} - P_{decision}$).
  - `EmergencyHaltTool` for manual or automated killswitch.

---

## 16. Historical Provenance Correction (2026-07-31)
- An integration run executed on `2026-07-31` after that date had already passed.
- Initially mislabeled as forward evidence; reclassified to `PAPER_RUNTIME_HISTORICAL_INTEGRATION_TEST` (`COUNTS_TOWARD_FORWARD_BLOCK = FALSE`).

---

## 17. Historical Operational Dress Rehearsal (2026-09-01)
- Replayed historical session `2026-09-01` through the full forward runtime.
- **Result**: 299 raw symbols ingested -> 280 eligible -> 15 scanner survivors -> CAUTION gate -> 0 trades (no setup cleared 30 bps net hurdle). Clean reconciliation ($1,000 -> $1,000).

---

## 18. Missed-Opportunity Diagnostic & Blind Historical Week
- **Missed Opportunity Audit**: 383 historical rejections evaluated; filtering provided **`+$89.34` net benefit** (rejected pool PF = 0.77).
- **Blind Historical Week (May 2026)**:
  - 5 sessions (`2026-05-01` to `2026-05-07`), seed `20260918`, trained $\le$ `2026-04-30`.
  - Primary Frozen Book (`BOOK_FROZEN_30`): 4 trades, 1 cash day, Net P&L **`-$1.98`**, PF `0.76`.
  - INTC traded on 3 sessions (+$5.75 on Day 1); avoided losing MRK trade on Day 4.

---

## 19. Session 1 True Forward Paper Execution (2026-09-18)
- **Session ID**: `TRUE_FORWARD_20260918_PCV1_df3c84`
- **Host**: Unity HPC Cluster (`uri-cpu032`, Slurm Job `64571170`).
- **Policy**: `FORWARD_PAPER_POLICY_V1` (SHA-256: `9c2bc9f33a93...`).
- **Result**: CAUTION gate -> 15 candidates evaluated -> 0 trades cleared 30 bps hurdle -> 100% Flat Cash -> Clean Reconciliation.
- **Classification**: `FORWARD_PAPER_TRADING` (`COUNTS_TOWARD_FORWARD_BLOCK = TRUE`). Progress: **1 / 20 Sessions**.
