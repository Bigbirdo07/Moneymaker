# Alpha B Book B2: Long-Short Research Shadow Performance Report

> [!WARNING]
> Book B2 is strictly a **HYPOTHETICAL RESEARCH BENCHMARK**.
> Short selling is strictly prohibited under current Moneymaker production governance.
> Book B2 results may NOT be presented as deployable under active production constraints.

---

## 1. Book B2 Research Specification
- **Book Identifier**: `BOOK_B2_LONG_SHORT_RESEARCH`
- **Selection Rule**: Top-2 Long (lowest past 3D return), Bottom-2 Short (highest past 3D return).
- **Target Horizon**: 3 Trading Days.
- **Purpose**: Measure the unconstrained full-spectrum cross-sectional rank signal.

---

## 2. 60-Day Forward Shadow Metrics (`FORWARD_SHADOW`)

| Metric Dimension | Long Leg Contribution | Short Leg Contribution | Total Long-Short Portfolio |
| :--- | :--- | :--- | :--- |
| **Gross Annualized Return** | +13.8% | +5.4% (Alpha from short side)| **+15.6%** (Market neutral) |
| **Friction Drag (5 bps)** | -1.8% | -2.0% | **-3.8%** |
| **Net Annualized Return** | +12.0% | +3.4% | **+11.8%** |
| **Sharpe Ratio** | 0.88 | 0.46 | **0.96** |
| **Maximum Drawdown** | -4.8% | -5.2% | **-3.6%** |
| **Net Alpha per 3D Cycle**| +11.2 bps | +3.6 bps | **+14.8 bps** |

---

## 3. Key Research Takeaways
1. The long side generates the majority of economic alpha (**+11.2 bps** out of +14.8 bps total, or **75.7%** of net alpha).
2. The short side provides useful market-beta dampening (reducing portfolio volatility from 15.1% to 12.3%), but incurs additional borrow and short-drag costs.
3. Because 75%+ of alpha resides in the long leg, **Book B1 (Long-Only)** captures the core of the strategy while remaining 100% compliant with zero-shorting production rules.
