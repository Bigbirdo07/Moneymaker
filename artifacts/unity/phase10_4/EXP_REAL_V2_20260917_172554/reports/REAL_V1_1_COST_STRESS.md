# Real Market Data Cost Sensitivity & Friction Stress Report

## 1. Executive Summary
To evaluate real-world friction sensitivity, the frozen V1.1 engine was evaluated under scaled friction multipliers ($1.0\times$ to $3.0\times$ baseline spread, slippage, and commission) across 43 real market sessions (`2026-03-01` to `2026-04-30`).

| Friction Tier | Cost Multiplier | Effective Spread (bps) | Net Return (%) | Net P&L ($) | Win Rate (%) | Gross Profit Factor | Total Friction ($) | Breakeven Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1.0x Baseline** | 1.0x | 3.0 bps | **-6.40%** | **-$64.04** | 41.9% | 1.06 | $82.74 | **DEFICIT** |
| **1.5x Elevated** | 1.5x | 4.5 bps | **-10.98%** | **-$109.80** | 41.9% | 1.03 | $117.33 | **DEFICIT** |
| **2.0x Harsh** | 2.0x | 6.0 bps | **-14.34%** | **-$143.37** | 37.2% | 1.03 | $150.21 | **DEFICIT** |
| **3.0x Extreme** | 3.0x | 9.0 bps | **-18.80%** | **-$188.03** | 31.4% | 1.13 | $218.14 | **DEFICIT** |

---

## 2. Friction Breakeven Analysis
1. **1.0x Baseline Costs**: Friction ($82.74) exceeds gross profits ($18.70), yielding a net deficit of **-$64.04 (-6.40%)**.
2. **1.5x Elevated Friction**: Total friction rises to $117.33, resulting in **-$109.80 (-10.98%)**.
3. **2.0x Harsh Execution**: Net return declines to **-$143.37 (-14.34%)**.
4. **3.0x Extreme Stress**: Net return is **-$188.03 (-18.80%)**.
5. **Conclusion**: Because raw intraday gross alpha on 1-minute bars is ~0.64–1.91 bps while IEX round-trip friction is ~6.5 bps, high-frequency intraday turnover generates negative net compounding on real market data.
