# Alpha B Forward Execution Cost & Turnover Decomposition Report

## 1. Cost Modeling Specification
For Alpha B forward shadow tracking across 60 trading days:
- **Execution Timing**: 09:30:00 EST market open / 5m VWAP on day $T+1$ following 16:05 EST signal generation on day $T$.
- **Spread Assumption**: $2.0$ bps (mega-cap top-of-book at open).
- **Execution Slippage**: $1.5$ bps.
- **Impact Cost**: $1.0$ bps.
- **Fees & Commissions**: $0.5$ bps.
- **Total Round-Trip Friction per Rebalance Cohort**: **$5.0$ bps**.

---

## 2. Forward Cost Drag vs Alpha Capture

| Parameter | Book B1 (Long-Only) | Book B2 (Long-Short) | Benchmark Reference |
| :--- | :--- | :--- | :--- |
| **Gross Alpha per 3D Cohort** | **+16.2 bps** | **+18.6 bps** | Historical: +21.4 bps |
| **Friction Drag per Cohort** | **-5.0 bps** | **-5.0 bps** | Modeled invariant |
| **Net Alpha per 3D Cohort** | **+11.2 bps** | **+13.6 bps** | Historical: +16.4 bps |
| **Annualized Cost Drag** | **-3.6%** | **-3.8%** | 18% daily turnover |
| **Cost Break-Even Multiplier** | **$3.24\times$** | **$3.72\times$** | Wide margin |

---

## 3. Overnight Gap Separation
- Overnight market gap is treated as market exposure return, not execution slippage.
- Average overnight gap across 60 days: $+0.04\%$ (consistent with long-term equity risk premium).
