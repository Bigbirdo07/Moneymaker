# Tier 3 Cost Margin & Stress Sensitivity Report

## 1. Cost Margin Compression Analysis
As capital scaled across tiers, gross alpha remained steady (+4.87 to +4.92 bps), while total canonical friction increased from 3.35 bps to 3.76 bps.

| Tier / Capital | Gross Alpha | Friction | Net Alpha | Cost Buffer (Gross - Friction) | Cost Break-Even Multiplier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 0 ($1k)** | +4.92 bps | 3.35 bps | +1.57 bps | **1.57 bps** | **1.47x** |
| **Tier 1 ($2.5k)**| +4.88 bps | 3.41 bps | +1.47 bps | **1.47 bps** | **1.43x** |
| **Tier 2 ($5k)** | +4.89 bps | 3.58 bps | +1.31 bps | **1.31 bps** | **1.37x** |
| **Tier 3 ($10k)** | **+4.87 bps** | **3.76 bps** | **+1.11 bps** | **1.11 bps** | **1.30x** |

---

## 2. Tier 3 Cost-Stress Sensitivity Matrix

$$\text{Break-Even Cost Multiplier} = \frac{\text{Gross Alpha (4.87 bps)}}{\text{Base Friction (3.76 bps)}} = \mathbf{1.295\times \approx 1.30\times}$$

| Friction Multiplier | Effective Friction (bps) | Net Expectancy (bps) | Absolute Retention % | Profit Factor | Viability Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1.00x (Base Costs)** | 3.76 bps | **+1.11 bps** | **70.7%** | **1.14** | **VIABLE (WATCH CAPACITY)** |
| **1.10x Costs** | 4.14 bps | **+0.73 bps** | **46.5%** | **1.08** | **DEGRADED CAPACITY** |
| **1.20x Costs** | 4.51 bps | **+0.36 bps** | **22.9%** | **1.04** | **FRAGILE EDGE** |
| **1.25x Costs** | 4.70 bps | **+0.17 bps** | **10.8%** | **1.02** | **MARGINAL VIABILITY** |
| **1.30x (Break-Even)** | 4.89 bps | **-0.02 bps** | **-1.3%** | **1.00** | **CAPACITY EXCEEDED** |
| **1.50x Costs** | 5.64 bps | **-0.77 bps** | **-49.0%** | **0.88** | **UNVIABLE** |
| **2.00x Costs** | 7.52 bps | **-2.65 bps** | **-168.8%**| **0.65** | **SEVERE LOSS** |

---

## 3. Governance Conclusion on Cost Buffers
- Tier 3 retains an adequate safety buffer (+1.11 bps / $1.30\times$ multiplier) under normal and mild stress conditions.
- However, if market spreads widen by $>30\%$ simultaneously with elevated slippage, net edge will evaporate.
- Therefore, $10,000 USD is near the practical upper bound of high-confidence capacity under current execution rules.
