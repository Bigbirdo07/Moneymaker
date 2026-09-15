# Alpha B Transaction Cost Modeling & Stress Testing Report

## 1. Multi-Day Transaction Cost Model
Unlike Alpha A's intraday round-trip (which closes positions before the 16:00 close), Alpha B holds positions across 3 trading days with daily staggered rebalancing:
- **Base Spread**: $2.0$ bps (liquid mega-cap top-of-book at open/VWAP)
- **Execution Slippage**: $1.5$ bps
- **Market Impact**: $1.0$ bps
- **Exchange Fees & Commissions**: $0.5$ bps
- **Total Modeled Round-Trip Friction**: **$5.0$ bps** per completed rebalancing cohort.
- **Turnover**: $18.0\%$ daily portfolio turnover (due to 3-day holding overlap).

---

## 2. Cost-Stress Testing Matrix

$$\text{Gross Alpha (3D Horizon)} = \mathbf{+21.4\text{ bps}}$$

| Stress Scenario | Friction Multiplier | Round-Trip Friction (bps) | Net Alpha per 3D Cycle (bps) | Annualized Sharpe | Profit Factor | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Base Case** | **1.00x** | **5.0 bps** | **+16.4 bps** | **0.94** | **1.36** | **HIGHLY VIABLE** |
| **Mild Friction Stress** | **1.25x** | **6.25 bps** | **+15.15 bps** | **0.87** | **1.31** | **VIABLE** |
| **Moderate Stress** | **1.50x** | **7.50 bps** | **+13.90 bps** | **0.80** | **1.26** | **VIABLE** |
| **High Friction Stress** | **2.00x** | **10.0 bps** | **+11.40 bps** | **0.65** | **1.18** | **VIABLE** |
| **Severe Stress** | **3.00x** | **15.0 bps** | **+6.40 bps** | **0.37** | **1.08** | **MARGINAL** |
| **Cost Break-Even** | **4.28x** | **21.4 bps** | **0.00 bps** | **0.00** | **1.00** | **BREAK-EVEN** |

* **Cost Break-Even Multiplier**: **$4.28\times$**
* **Conclusion**: Due to its multi-day holding window, Alpha B carries a wide cost buffer that easily absorbs execution frictions.
