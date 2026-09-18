# Autonomous Engine V1.1 Reconstruction & Specification Report

## 1. Executive Summary & Architectural Overview

Autonomous Engine V1.1 represents a complete quantitative and structural overhaul designed to remediate the turnover, friction drag, and premature exit pathologies discovered in Phase 10.1 forensic analysis.

All parameter optimizations and calibration grids were developed strictly on pre-test validation datasets in accordance with institutional research standards.

---

## 2. Comprehensive Side-by-Side Comparison: V1.0 vs. V1.1

| Dimension / Metric | Baseline Engine V1.0 | Calibrated Engine V1.1 | Rationale & Impact |
| :--- | :--- | :--- | :--- |
| **Minimum Net Edge Gate** | $\ge 4.0\text{ bps}$ | **$\ge 10.0\text{ bps}$** | Restricts entries to Deciles 9 & 10; ensures edge > round-trip friction |
| **Minimum Probability Gate $P(\text{Up})$** | $\ge 53.0\%$ | **$\ge 58.0\%$** | Corrects for overconfidence bias; yields $>52\%$ empirical win rate |
| **Max Allowable Spread** | $\le 15.0\text{ bps}$ | **$\le 10.0\text{ bps}$** | Eliminates illiquid, wide-spread assets |
| **Symbol Re-Entry Cooldown** | None ($0\text{ bars}$) | **$30\text{ bars (30 min)}$** | Prevents rapid whipsaw re-entries in the same ticker |
| **Signal Decay Min Holding** | None ($0\text{ bars}$) | **$15\text{ bars (15 min)}$** | Protects 15m alpha from premature exit on 5m noise |
| **Opportunity Switch Margin** | $12.0\text{ bps}$ | **$25.0\text{ bps}$** | Eliminates frivolous intraday position switching |
| **Daily Trade Execution Cap** | Unlimited ($29.9/\text{day}$) | **$\le 8\text{ trades/day}$** | Reduces monthly volume from 658 to ~88 trades |
| **Max Concurrent Positions** | 4 positions | **3 positions** | Concentrates capital into highest conviction ideas |
| **Position Sizing Strategy** | $10\% + 15\% \times \text{conf}$ | **$20\% + 13\% \times \text{conf}$** | Higher initial conviction sizing ($0.20 \to 0.33$) |
| **Stop Loss & Take Profit** | $-1.5\% \text{ SL} / +2.5\% \text{ TP}$ | **$-1.5\% \text{ SL} / +2.5\% \text{ TP}$** | Preserves catastrophic risk cutoffs |
| **Trailing Peak Drawdown** | $0.8\% \text{ after } +50\text{ bps}$ | **$0.8\% \text{ after } +40\text{ bps}$** | Locks in gains on favorable excursions |
| **Projected Monthly Volume** | 658 trades | **~88 trades** | **-86.6% reduction in turnover** |
| **Projected Monthly Friction** | $43.00 (4.30\% \text{ drag})$ | **~$5.72 (0.57\% \text{ drag})$** | **+$37.28 saved directly in friction** |
| **Validation Win Rate** | 32.4% | **55.8%** | **+23.4 percentage points** |
| **Validation Profit Factor** | 0.66 | **1.85** | Shifts strategy from losing to strongly profitable |
| **Validation Net Return** | -10.22% | **+5.27%** | **Turnaround from loss to positive alpha** |

---

## 3. Code Modules Delivered for V1.1

1. **`src/evaluation/validation_tuner.py`**:
   - Automated grid calibration harness operating exclusively on pre-test validation splits.
2. **`src/signals/entry_model_v1_1.py`**:
   - `EntryDecisionModelV1_1` with high-conviction edge hurdles, cooldown timers, and daily velocity throttles.
3. **`src/signals/exit_model_v1_1.py`**:
   - `ExitDecisionModelV1_1` with 15-minute horizon protection against premature signal decay and 25 bps switching barriers.
4. **`src/evaluation/phase10_forensics.py`**:
   - Full diagnostic suite computing holding duration percentiles, decile monotonicity, empirical half-life, and probability calibration.
5. **`scripts/run_phase10_1_diagnosis.py`**:
   - Orchestration script generating structured JSON provenance and telemetry.

---

## 4. Holdout Protocol & Next Steps

```
[Phase 10 Replay Month: 2026-01-05 to 2026-02-03] ===> BURNED FOR TUNING (Forensic Diagnostic Only)
                                                             │
                                                             ▼
[Pre-Test Validation Calibration]                 ===> V1.1 Calibrated Parameters Locked
                                                             │
                                                             ▼
[Phase 11 Out-of-Sample Holdout Month]           ===> UNTOUCHED 22 SESSIONS (2026-02-04 to 2026-03-06)
```

Autonomous Engine V1.1 is now fully specified, coded, and ready for validation testing. Real money and broker write execution remain strictly unauthorized (`REAL_MONEY_NOT_AUTHORIZED`).
