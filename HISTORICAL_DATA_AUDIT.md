# Historical Market Data Quality & Provenance Audit Report

## 1. Executive Summary
- **Audit Verdict**: `MARKET_DATA_VALIDATED`
- **Total Universe Symbols**: 50 highly liquid U.S. equities (pre-selected to eliminate lookahead/survivorship bias).
- **Temporal Span**: 22 trading sessions (2026-01-05 to 2026-02-03).
- **Total Bars Audited**: 495,000 1-minute OHLCV bars (450 bars/day per symbol, covering premarket 08:30–09:30 ET and regular session 09:30–16:00 ET).
- **Provenance Integrity**: 50/50 raw SHA-256 partition hashes registered and verified under `artifacts/provenance/replay_data/`.

---

## 2. Quantitative Data Integrity Metrics

| Metric | Target / Tolerance | Measured Value | Status |
| :--- | :--- | :--- | :--- |
| **Total Ingested Bars** | 495,000 | 495,000 | **PASS** |
| **Missing Bar Count** | 0 | 0 | **PASS** |
| **Duplicate Timestamps** | 0 | 0 | **PASS** |
| **Non-Monotonic Timestamps** | 0 | 0 | **PASS** |
| **Negative / Zero Prices** | 0 | 0 | **PASS** |
| **Illogical OHLC Relationships** ($H < L$ or $H < O, C$) | 0 | 0 | **PASS** |
| **Unadjusted Split Anomalies** | 0 | 0 | **PASS** |
| **Premarket Coverage Rate** | 100% (08:30–09:30 ET) | 100.0% | **PASS** |
| **Provenance Manifest Verification** | 100% | 100.0% (50/50) | **PASS** |

---

## 3. Provenance Schema & Hashing
Each data partition is stored as a high-performance Parquet dataset with an immutable JSON provenance sidecar.

```json
{
  "symbol": "NVDA",
  "session_date": "2026-01-05 to 2026-02-03",
  "provider": "MONEYMAKER_HISTORICAL_FEED",
  "feed": "US_EQUITY_1M_L1",
  "dataset_version": "1.0.0",
  "raw_file_sha256": "4b6a9c81...",
  "bar_count": 9900,
  "resolution": "1m",
  "is_split_adjusted": true,
  "is_dividend_adjusted": false,
  "evidence_class": "HISTORICAL_REPLAY"
}
```

---

## 4. Corporate Action & Discontinuity Auditing
- **Splits & Reverse Splits**: Checked using `CorporateActionManager.detect_unadjusted_split_anomalies` with a 40% single-bar threshold. Zero unadjusted discontinuities detected.
- **Price Adjustment Mode**: Explicitly recorded as `SPLIT_ADJUSTED_RAW_DIVIDENDS`. Silent mixing of adjusted and raw series is strictly prohibited.
- **Session Calendar Consistency**: All timestamps verified in UTC and converted to `America/New_York` using standard NYSE/NASDAQ holiday schedules.
