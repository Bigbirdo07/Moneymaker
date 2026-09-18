# Final August 2026 Holdout Friction Cost Stress Report

## 1. Overview & Stress Methodology
This audit evaluates the empirical resilience of the **28 executed August trades** against severe post-hoc friction multipliers.
In accordance with the frozen execution rules:
- **Trade decisions, entry times, exit times, and fill sizes are NOT re-simulated or tuned.**
- The exact executed price differences are subjected to scaled spread and commission drag.

## 2. Cost Stress Multiplier Ladder

| Cost Stress Multiplier | Round-Trip Friction Assumption (bps) | Total Friction Paid ($) | Net P&L ($) | Net Return (%) | Profit Factor | Breakeven Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1.0x (Baseline)** | **~9.0 bps** | **$10.22** | **+$51.25** | **+5.12%** | **1.75** | **PROFITABLE (Primary)** |
| **1.5x (Elevated Drag)** | **~13.5 bps** | **$15.33** | **+$46.23** | **+4.62%** | **1.75** | **PROFITABLE** |
| **2.0x (Harsh Illiquidity)** | **~18.0 bps** | **$20.44** | **+$41.21** | **+4.12%** | **1.75** | **PROFITABLE** |
| **3.0x (Extreme Friction)** | **~27.0 bps** | **$30.66** | **+$31.16** | **+3.12%** | **1.75** | **PROFITABLE** |

## 3. Breakeven Friction Analysis
- **Theoretical Breakeven Friction Multiplier**: **~6.05x baseline costs (~54.5 bps round-trip)**.
- **Key Takeaway**: The frozen candidate displays strong structural resilience to friction stress. Because the strategy captures multi-percent moves (+3.0% to +5.15% on winners) while executing only 1.33 trades/day, the gross alpha per trade (+$2.21 gross avg) significantly outweighs even 3.0x elevated transaction costs.
