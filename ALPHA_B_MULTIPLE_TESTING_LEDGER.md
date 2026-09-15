# Alpha B Multiple Testing & Experiment Ledger

## 1. Governance Rule
All experimental hypotheses, model architectures, and horizon evaluations conducted under the `ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL` family are permanently logged to prevent hidden degrees of freedom.

---

## 2. Experiment Ledger

| Experiment ID | Model / Hypothesis Description | Target Horizon | Spearman Rank IC | Rank IC p-value | Gross Alpha (bps) | DSR p-value | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ALPHA_B_EXP_001` | Simple 3D Reversal Baseline | 3D | +0.038 | 0.012 | +18.5 bps | 0.048 | Baseline Logged | Initial non-ML reference |
| `ALPHA_B_EXP_002` | 3D Reversal + Market Relative Strength | 3D | +0.042 | 0.008 | +22.1 bps | 0.041 | Baseline Logged | Adding SPY relative adjustment |
| `ALPHA_B_EXP_003` | Overnight Gap Fading Hypothesis | 1D | +0.029 | 0.035 | +12.4 bps | 0.082 | Exploration | Requires tighter spread filter |
| `ALPHA_B_EXP_004` | 5D Structural Reversal Hypothesis | 5D | +0.034 | 0.021 | +26.8 bps | 0.054 | Exploration | Lower trade frequency |

---

## 3. Cumulative Multiple Testing Audit

- **Total Experiments Registered**: 4
- **Active Family**: `ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL`
- **Family Status**: `HISTORICAL_RESEARCH_ONLY`
- **Live Permission**: **BLOCKED (0 / 0 Live Permissions)**
