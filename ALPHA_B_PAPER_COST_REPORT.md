# Alpha B Broker Paper Cost Margin & Sensitivity Report (Phase 7A Track B)

**Strategy**: `ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL`  
**Base Friction**: 5.0 bps / 3D cycle (Spread: 2.0 bps, Slippage: 1.5 bps, Impact: 1.0 bps, Fees: 0.5 bps)  
**Base Gross Alpha**: +16.2 bps / 3D cycle

---

## 1. Cost Stress Matrix

| Cost Multiplier | Total Friction (bps) | Net Cycle Expectancy (bps) | Annualized Net Return (%) | Cost Break-Even Margin | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1.00x (Base)** | **5.00** | **+11.20** | **+10.2%** | **3.24x** | `ROBUST` |
| **1.25x** | **6.25** | **+9.95** | **+9.1%** | **2.59x** | `ROBUST` |
| **1.50x** | **7.50** | **+8.70** | **+7.9%** | **2.16x** | `HEALTHY` |
| **2.00x** | **10.00** | **+6.20** | **+5.6%** | **1.62x** | `ACCEPTABLE`|
| **3.00x** | **15.00** | **+1.20** | **+1.1%** | **1.08x** | `MARGINAL` |

---

## 2. Cost Break-Even Multiplier

$$\mathbf{ALPHA\_B\_COST\_BREAK\_EVEN\_MULTIPLIER} = \frac{\text{Gross Alpha (16.20 bps)}}{\text{Base Friction (5.00 bps)}} = \mathbf{3.24\times}$$

$$\text{Zero Net Expectancy Point} = \mathbf{16.20\text{ bps friction / cycle}}\quad (3.24\times\text{ cost expansion})$$

> [!NOTE]
> Unlike intraday strategies (where Alpha A operates at a 1.30x multiplier due to ~15-minute holding periods and frequent turnover), Alpha B's 3-day holding period creates significantly lower turnover drag (~18% daily turnover), resulting in a substantial cost buffer of **$3.24\times$**.
