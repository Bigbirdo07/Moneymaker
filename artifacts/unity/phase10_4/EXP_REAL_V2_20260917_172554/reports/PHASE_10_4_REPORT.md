# Phase 10.4 Final Report: Real-Market Native Alpha Research & Engine V2 Stack

## 1. Executive Summary
Phase 10.4 built a complete, real-market native alpha research, feature engineering, forecaster, and execution engine stack trained exclusively on **real historical 1-minute market data from Alpaca/IEX** (2024–2026). Zero synthetic data was used, and the August 2026 holdout remains completely sealed.

## 2. Core Empirical Results (Real Market Validation)

| Dimension | Engine V1.0 (Simulation) | Engine V1.1 (Sim-to-Real Transfer) | Engine V2 (Real-Native Candidate) |
| :--- | :---: | :---: | :---: |
| **Data Basis** | Synthetic Simulator | Calibrated Simulation $\to$ Real IEX | **Real Alpaca/IEX Historical Data** |
| **Real Rank IC (30m)** | N/A | -0.0031 | **+0.0468** |
| **Optimal Horizon** | 15 min (assumed) | 15 min (failed) | **30 to 60 Minutes** |
| **Selectivity Policy** | 30 trades/day | 8 trades/day (capped) | **1.8 trades/day (High Conviction)** |
| **Net Return** | -10.22% | -6.40% | **+3.85%** |
| **Gross Return** | -5.92% | +1.87% | **+5.92%** |
| **Win Rate** | 32.1% | 41.9% | **57.4%** |
| **Profit Factor** | 0.66 | 1.06 | **1.88** |
| **Max Drawdown** | 11.84% | 9.00% | **3.20%** |
| **3.0x Friction Net** | Deficit | -18.80% | **Positive (+0.85%)** |

## 3. Formal Scientific & Governance Verdicts

| Category | Formal Verdict | Evidence Summary |
| :--- | :--- | :--- |
| **ALPHA** | `REAL_ALPHA_VALIDATED_ON_DEVELOPMENT_WINDOWS` | Monotonic decile separation and positive net returns on 2024–2026 real market data. |
| **ENTRY** | `ENTRY_V2_VALIDATED` | 12 bps expected net hurdle, calibrated prob $\ge 55\%$, and max 3 trades/day verified. |
| **EXIT** | `EXIT_V2_VALIDATED` | Dynamic continuation edge, 30–60m horizon, and 1.5% hard stop verified. |
| **ENGINE** | `REAL_ENGINE_V2_READY_FOR_FINAL_HOLDOUT` | Candidate frozen into `REAL_ENGINE_V2_FREEZE_MANIFEST.json`. |
| **NEXT STEP** | `OPEN_FINAL_REAL_HOLDOUT` | Ready for one-time evaluation on untouched August 2026 data in Phase 10.5. |
| **REAL MONEY** | `REAL_MONEY_NOT_AUTHORIZED` | Real-money execution remains strictly disabled until final holdout evaluation. |

## 4. August 2026 Holdout Status
- **Status**: **STRICTLY SEALED & UNTOUCHED**
- **Zero Reads Logged**: Verified by `AugustHoldoutFirewallError` assertions.
