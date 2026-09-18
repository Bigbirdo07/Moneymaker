# Phase 11A Real Historical Data Provenance & Window Mapping

## 1. Overview & Provenance Standard
- **Universe**: Canonical Standard 50 Equities (`STANDARD_50_UNIVERSE`).
- **Data Provider**: `ALPACA`
- **Data Feed**: `IEX`
- **Evidence Class**: `REAL_HISTORICAL_MARKET_DATA`
- **Temporal Coverage**: `2024-01-02` to `2026-08-31` (32 consecutive calendar months, ~575 trading sessions, 50 symbols, 1-minute OHLCV bars).
- **Synthetic Contamination**: **0.00% (Zero synthetic bars or artificial fill)**.

---

## 2. Chronological Window Classification

| Window Identifier | Calendar Range | Session Count | Formal Classification | Operational Role in Phase 11A |
| :--- | :---: | :---: | :--- | :--- |
| **2024 Baseline** | `2024-01-02` to `2024-12-31` | 252 sessions | `TRAIN_BASELINE_PRIOR_HISTORY` | Base in-sample historical training pool for expanding walk-forward windows. |
| **2025 Rolling OOS** | `2025-01-02` to `2025-12-31` | 250 sessions | `ELIGIBLE_FRESH_OOS_VALIDATION` | **12 independent, untouched out-of-sample monthly evaluation windows** evaluated via expanding origin. |
| **2026 Development** | `2026-01-02` to `2026-05-29` | 104 sessions | `USED_MODEL_VALIDATION` | Historical validation set used during Phase 10.4 candidate ranking. |
| **2026 Secondary** | `2026-06-01` to `2026-07-31` | 43 sessions | `USED_SECONDARY_VALIDATION` | Secondary validation set evaluated in Phase 10.4 (+5.76% net return, 107 trades). |
| **2026 August Holdout** | `2026-08-03` to `2026-08-31` | 21 sessions | `BURNED_HOLDOUT_DO_NOT_REUSE` | Permanently burned final holdout evaluated in Phase 10.5 (+5.12% net return, 28 trades). **Sealed from all model tuning and training.** |

---

## 3. Rolling-Origin Walk-Forward Design

Each of the 12 evaluation months in 2025 is evaluated strictly out-of-sample:
1. **Expanding Window Training**: The multi-horizon forecaster is trained strictly on observations $[t_0, t_{T-1}]$, where $t_{T-1}$ is the final bar of the preceding calendar month.
2. **Purge & Embargo**: No observation from month $T$ or future dates is exposed to the model during training, feature scaling, or threshold calibration.
3. **Single-Pass Evaluation**: Replay on month $T$ executes once under the frozen strategy rules (`RealMarketEntryModelV2`, `RealMarketExitModelV2`, `RealMarketAllocatorV2`).
4. **Machine-Readable Audit**: All decisions, fills, exits, frictions, and signals are written to partitioned monthly Parquet ledgers.
