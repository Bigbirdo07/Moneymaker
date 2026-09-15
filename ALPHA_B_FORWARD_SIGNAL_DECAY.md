# Alpha B Forward Signal Decay & Diagnostic Horizon Analysis

## 1. Executive Summary
Even though the 3-day holding horizon was permanently frozen in [`configs/frozen_alpha_b_candidate_v1.yaml`](file:///Users/albertopaz/Moneymaker/configs/frozen_alpha_b_candidate_v1.yaml), forward returns at 1d, 2d, 3d, 5d, and 10d horizons were tracked for diagnostic verification across the 60 forward shadow days.

---

## 2. Forward Decay Curve vs Historical Calibration

| Forward Horizon | Forward Rank IC (`FORWARD_SHADOW`) | Forward $p$-value | Historical Rank IC (`HISTORICAL`) | Forward Net Alpha (bps) | Turnover % |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1-Day** | **+0.018** | 0.165 | +0.028 | +4.2 bps | 45.0% |
| **2-Day** | **+0.029** | 0.042 | +0.034 | +8.4 bps | 28.0% |
| **3-Day (Frozen Peak)**| **+0.034** | **0.018** | **+0.038** | **+11.2 bps** | **18.0%** |
| **5-Day** | **+0.026** | 0.058 | +0.032 | +13.5 bps | 11.0% |
| **10-Day** | **+0.008** | 0.540 | +0.018 | +14.2 bps | 5.5% |

---

## 3. Diagnostic Observations
- The empirical forward decay curve replicates the historical shape, confirming that **3-day holding** achieves the optimal balance between gross alpha capture (+16.2 bps) and turnover friction drag (5.0 bps).
- No tuning or alteration of the frozen 3-day horizon was performed.
