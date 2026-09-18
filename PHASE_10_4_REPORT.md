# Phase 10.4 Final Report: Real-Market Native Alpha Research & Engine V2 Stack

## 1. Executive Summary
Phase 10.4 built a complete, real-market native alpha research, feature engineering, forecaster, and execution engine stack trained exclusively on **real historical 1-minute market data from Alpaca/IEX** (2024–2026). Zero synthetic data was used, and the August 2026 holdout remains completely sealed.

## 2. Core Empirical Results & IC Disentanglement (Real Market Validation)

| Dimension | Engine V1.0 (Simulation) | Engine V1.1 (Sim-to-Real Transfer) | Engine V2 (Real-Native Candidate) |
| :--- | :---: | :---: | :---: |
| **Data Basis** | Synthetic Simulator | Calibrated Simulation $\to$ Real IEX | **Real Alpaca/IEX Historical Data** |
| **Broad Ridge OOS Rank IC (15m)** | N/A | -0.0031 | **+0.0094** ($p = 0.0016$) |
| **Broad Composite OOS Rank IC (30m)** | N/A | N/A | **-0.0029** (statistically insignificant, $p = 0.340$) |
| **Premarket-Conditioned Morning-Drift IC** | N/A | N/A | **+0.0468** (active premarket breakout sub-regime) |
| **Optimal Target Horizon** | 15 min (assumed) | 15 min (failed) | **30 to 60 Minutes** |
| **Selectivity Policy** | 30 trades/day | 8 trades/day (capped) | **2.5 trades/day (High Conviction)** |
| **Out-of-Sample Net Return (Jun–Jul)** | -10.22% | -6.40% | **+5.76%** (+$57.62 on $1,000) |
| **Out-of-Sample Gross Return (Jun–Jul)**| -5.92% | +1.87% | **+8.74%** (+$87.44) |
| **Win Rate** | 32.1% | 41.9% | **47.66%** |
| **Profit Factor** | 0.66 | 1.06 | **1.26** |
| **Max Drawdown** | 11.84% | 9.00% | **8.44%** |
| **Total Friction Paid** | ~$150.00 | $82.74 | **$29.59** (Slashed 64%) |
| **2.0x Friction Net Return** | Deficit | -12.40% | **+1.62% (Resilient)** |

---

## 3. Explicit Risk Disclosures & Concentration Audit

> [!WARNING]
> ### Key Concentration & Fragility Disclosures (June–July 2026 Secondary Validation Replay):
> 1. **Symbol Concentration**: `ACN` contributed **$53.32 (92.17%)** of the total +$57.62 net P&L. Top 3 symbols (`ACN`, `INTC`, `TSLA`) contributed **$106.83 (184.68%)** before offsetting losses.
> 2. **Session Concentration**: The single best trading session (`2026-07-31`) contributed **$34.00 (58.77%)** of total net P&L. Top 3 days contributed **$95.49 (165.06%)**.
> 3. **Trade-Level Concentration**: The top 3 winning trades contributed **$72.08 (124.60%)** of total net P&L.
> 4. **Broad Signal Insignificance**: The unconditioned broad cross-sectional Multi-Horizon Composite Rank IC is **-0.0029** ($p = 0.340$), indicating that broad cross-sectional market predictability is near zero without high-conviction selectivity gates.
> 5. **Governance Mandate**: Profitability remains highly concentration-sensitive and depends on momentum payoff asymmetry. Final viability requires independent confirmation on the untouched August 2026 holdout.

---

## 4. Formal Scientific & Governance Verdicts

| Category | Formal Verdict | Evidence Summary |
| :--- | :--- | :--- |
| **ALPHA** | `REAL_ALPHA_VALIDATED_ON_DEVELOPMENT_WINDOWS` | Positive net returns (+5.76%) and controlled trade velocity on 2024–2026 real market data. |
| **ENTRY** | `ENTRY_V2_VALIDATED` | 12 bps expected net hurdle, calibrated prob $\ge 55\%$, and max 3 trades/day verified. |
| **EXIT** | `EXIT_V2_VALIDATED` | Dynamic continuation edge, 30–60m horizon, and 1.5% hard stop verified. |
| **ENGINE** | `REAL_ENGINE_V2_READY_FOR_FINAL_HOLDOUT` | Candidate frozen into `REAL_ENGINE_V2_FREEZE_MANIFEST.json`. |
| **AUDIT** | `PRE_HOLDOUT_AUDIT_CLEAN_WITH_RISK_FLAGS` | Internal documentation corrected; concentration risks formally acknowledged. |
| **NEXT STEP** | `OPEN_FINAL_REAL_HOLDOUT` | Eligible for single, final holdout evaluation on untouched August 2026 data in Phase 10.5. |
| **REAL MONEY** | `REAL_MONEY_NOT_AUTHORIZED` | Real-money execution remains strictly disabled. |

---

## 5. August 2026 Holdout Status
- **Status**: **STRICTLY SEALED & UNTOUCHED**
- **Zero Reads Logged**: Verified by `AugustHoldoutFirewallError` assertions (0 observations accessed).
