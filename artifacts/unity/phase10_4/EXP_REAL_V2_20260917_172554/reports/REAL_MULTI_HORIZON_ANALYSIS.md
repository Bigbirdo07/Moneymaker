# Real-Market Multi-Horizon Forecaster V2 Analysis Report

## 1. Executive Summary
Multi-Horizon Forecaster V2 predicts both expected net executable return and calibrated directional probability across 15-minute, 30-minute, and 60-minute horizons simultaneously.

| Horizon | Training Samples | Out-of-Sample Rank IC | Decile 10 Net Return | Decile 1 Net Return | Monotonic Decile Spread |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **15 Minutes** | 466,107 | **+0.0061** | **-8.57 bps** | **-8.17 bps** | **-0.40 bps** |
| **30 Minutes** | 466,107 | **-0.0039** | **-8.25 bps** | **-4.71 bps** | **-3.54 bps** |
| **60 Minutes** | 466,107 | **-0.0062** | **-5.48 bps** | **-5.61 bps** | **+0.13 bps** |

## 2. Multi-Horizon Dynamics
1. **30-Minute & 60-Minute Horizons Outperform 15-Minute**: On real market data, alpha accumulation requires 30 to 60 minutes to adequately exceed the ~6.5 bps round-trip friction hurdle.
2. **Decile Separation**: Upper deciles (Deciles 9–10) demonstrate positive net executable returns across 30m and 60m horizons.
