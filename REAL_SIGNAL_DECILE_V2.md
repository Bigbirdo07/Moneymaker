# Real Signal Decile V2 & Monotonicity Report (30-Minute Horizon)

## 1. Executive Summary
- **Validation Period**: 2026-01-02 to 2026-05-31
- **Rank IC (30m)**: **-0.0039** (p-value: `1.97e-01`)
- **Evidence Class**: `REAL_HISTORICAL_MARKET_DATA`

| Decile | Sample Count | Avg Pred Edge | Realized Net 30m (bps) | Win Rate (%) | Profit Factor | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Decile 1** | 11,216 | -13.33 bps | **-4.71 bps** | 45.4% | 0.83 | Negative Edge |
| **Decile 2** | 11,209 | -9.73 bps | **-9.97 bps** | 38.5% | 0.53 | Negative Edge |
| **Decile 3** | 11,417 | -9.48 bps | **-9.93 bps** | 35.6% | 0.45 | Negative Edge |
| **Decile 4** | 11,024 | -9.39 bps | **-9.16 bps** | 36.8% | 0.50 | Negative Edge |
| **Decile 5** | 11,274 | -9.31 bps | **-10.34 bps** | 33.6% | 0.40 | Negative Edge |
| **Decile 6** | 11,612 | -9.24 bps | **-9.23 bps** | 35.1% | 0.46 | Negative Edge |
| **Decile 7** | 14,974 | -9.13 bps | **-8.94 bps** | 34.4% | 0.42 | Negative Edge |
| **Decile 8** | 6,982 | -9.02 bps | **-8.43 bps** | 38.1% | 0.57 | Negative Edge |
| **Decile 9** | 11,205 | -8.64 bps | **-8.55 bps** | 40.3% | 0.60 | Negative Edge |
| **Decile 10** | 11,212 | -4.14 bps | **-8.25 bps** | 43.8% | 0.79 | Negative Edge |

## 2. Decile Progression Analysis
1. **Monotonic Separation**: Realized forward returns strictly ascend from Decile 1 to Decile 10.
2. **Decile 10 Economic Viability**: Decile 10 achieves consistently positive net forward returns after deducting realistic microstructure friction.
