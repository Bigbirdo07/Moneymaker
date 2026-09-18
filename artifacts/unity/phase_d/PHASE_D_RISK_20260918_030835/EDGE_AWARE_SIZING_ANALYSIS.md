# Edge-Aware & Confidence Sizing Analysis

## 1. Sub-Linear Modulation
- $M_{\text{edge}} = \sqrt{\text{Edge}/25\text{bps}} \times (\text{Confidence}/0.60)$, clamped strictly to $[0.75, 1.25]$.
- Prevents destructive over-allocation to perceived 'sure-thing' setups while rewarding high-conviction signals.