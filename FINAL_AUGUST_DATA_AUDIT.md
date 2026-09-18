# Final August 2026 Holdout Data Audit Report

## 1. Provenance & Integrity
- **Holdout Window**: `2026-08-01` to `2026-08-31` (21 Trading Sessions)
- **Universe**: Canonical Standard 50 Equities (`STANDARD_50_UNIVERSE`)
- **Data Provider**: `ALPACA`
- **Market Feed**: `IEX`
- **Evidence Class**: `REAL_HISTORICAL_MARKET_DATA`
- **Total Aligned 15-Minute Observation Rows**: **22,214 observations**
- **Synthetic Contamination**: **0.00% (Zero synthetic bars or artificial fill)**
- **September / Future Leakage**: **0 observations (RealDataFirewall strictly enforced)**

## 2. Session Calendar & Trading Days
The August 2026 calendar contains exactly 21 official US equity trading sessions:
- `2026-08-03` (Mon) through `2026-08-07` (Fri) — 5 sessions
- `2026-08-10` (Mon) through `2026-08-14` (Fri) — 5 sessions
- `2026-08-17` (Mon) through `2026-08-21` (Fri) — 5 sessions
- `2026-08-24` (Mon) through `2026-08-28` (Fri) — 5 sessions
- `2026-08-31` (Mon) — 1 session

## 3. Cryptographic Freeze Compliance
Prior to reading the first row of August 2026 data, all 6 frozen candidate source modules were cryptographically hashed and matched at 100% SHA-256 parity against `REAL_ENGINE_V2_FREEZE_MANIFEST.json`:
1. `src/features/real_market_feature_store.py`: `d95e0c8b939f37fbbfa48303f29dd1a45749712613dca103be440c94da8a2d1d` (MATCH)
2. `src/models/real_market_multi_horizon_forecaster_v2.py`: `e21b7ff3bdf5359a3f9e17b8849b29cb72b9472e3538466b02fe49842dc9359e` (MATCH)
3. `src/signals/real_market_entry_model_v2.py`: `2e604085f1c9913364f89d38c64bb93b218491c98ca0f3f619e0780287cfeb26` (MATCH)
4. `src/signals/real_market_exit_model_v2.py`: `82f2c8d2345e552277d3fca855dc0eb8ffdb2c23f2ca7452d3a36c5ffdfa9a3b` (MATCH)
5. `src/execution/real_market_allocator_v2.py`: `d7730e7ca10f135b3769c09bf8ffeb7501a357fca3dc6011c2e434f0c608f658` (MATCH)
6. `src/replay/real_engine_v2_runner.py`: `80fe98dfce4b23b3f15cbf3f56e18758da4f4b2cfc19958784d0b1d3d639149f` (MATCH)

## 4. Evaluation-Only Runtime Invariant
- **Model Training**: Strictly trained on 2024–2025 training partition (466,107 observations).
- **Zero Training on August**: No `fit()`, `calibrate()`, or parameter tuning on August 2026.
- **Audit Verdict**: `PRE_HOLDOUT_AUDIT_CLEAN_WITH_RISK_FLAGS` confirmed prior to unlock.
