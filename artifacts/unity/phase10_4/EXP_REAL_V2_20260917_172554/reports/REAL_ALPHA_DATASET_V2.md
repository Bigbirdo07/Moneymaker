# Real Alpha Dataset V2 Architecture & Partition Specification

## 1. Dataset Overview
Real Alpha Dataset V2 forms the empirical foundation for Phase 10.4 alpha research, multi-horizon modeling, and execution policy calibration.

- **Total Observations**: 9,999,663 1-minute bars
- **Securities**: 50 fixed canonical equities (`STANDARD_50_UNIVERSE`)
- **Date Coverage**: `2024-01-02` to `2026-07-31`

## 2. Canonical Chronological Partitions

| Partition | Date Range | Calendar Span | Purpose | Status |
| :--- | :---: | :---: | :--- | :---: |
| **TRAIN** | `2024-01-02` to `2025-12-31` | 24 Months (2 Years) | Baseline & Forecaster Training | Open |
| **WALK-FORWARD / VAL** | `2026-01-02` to `2026-05-31` | 5 Months | Purged Walk-Forward & Selectivity Calibration | Open |
| **SECONDARY VAL** | `2026-06-01` to `2026-07-31` | 2 Months | Out-of-Sample Engine V2 Candidate Testing | Open |
| **FINAL HOLDOUT** | `2026-08-01` to `2026-08-31` | 1 Month | Untouched Final Evaluation (Phase 10.5) | **SEALED** |

## 3. Storage & Schema
- **Path**: `data/processed/alpaca_extended_1m/{symbol}_1m.parquet`
- **Columns**: `timestamp_utc`, `timestamp_et`, `symbol`, `open`, `high`, `low`, `close`, `volume`, `trade_count`, `vwap`, `canonical_symbol`, `feed`, `provider`, `evidence_class`
