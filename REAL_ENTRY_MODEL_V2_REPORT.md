# Real-Market Entry Model V2 Specification Report

## 1. Entry Threshold Gates
- **Minimum Expected Net Edge**: **12.0 bps** (must clear all friction plus positive buffer)
- **Minimum Calibrated Probability**: **55.0%** ($P(\text{Net Return} > 0)$)
- **Daily Trade Cap**: **3 trades/day maximum** (prevents overtrading)
- **Re-Entry Cooldown**: **30 bars (30 minutes)** on same security
- **Position Cap**: **2 concurrent positions maximum**
- **CASH Policy**: Default to CASH if conditions not met
