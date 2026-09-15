# Alpha B Target Returns & Multi-Horizon Research Specification

## 1. Candidate Target Horizons

Alpha B evaluates five discrete forward holding horizons:

$$\text{TargetReturn}_{k}(t) = \frac{\text{Close}_{t+k}}{\text{Close}_{t}} - 1$$

| Target Identifier | Horizon ($k$) | Economic Motivation | Expected Turnover | Overlap Purge Window |
| :--- | :--- | :--- | :--- | :--- |
| `target_ret_1d` | 1 Trading Day | Overnight to next close mean-reversion | High (Daily rebalance) | 1 day |
| `target_ret_2d` | 2 Trading Days | Two-day inventory rebalancing | Moderate | 2 days |
| `target_ret_3d` | 3 Trading Days | Primary multi-day swing reversal | Moderate | 3 days |
| `target_ret_5d` | 5 Trading Days | 1-week structural mean-reversion | Low (Weekly rebalance)| 5 days |
| `target_ret_10d`| 10 Trading Days| 2-week cyclical adjustment | Very Low | 10 days |

---

## 2. Return Target Formulations

For each horizon $k$, four target return formulations are evaluated:

1. **Raw Forward Return**: $R_{\text{raw}} = \frac{C_{t+k}}{C_t} - 1$
2. **Market-Relative Return**: $R_{\text{mkt}} = \left(\frac{C_{t+k}}{C_t} - 1\right) - \left(\frac{C_{\text{SPY}, t+k}}{C_{\text{SPY}, t}} - 1\right)$
3. **Sector-Relative Return**: $R_{\text{sec}} = \left(\frac{C_{t+k}}{C_t} - 1\right) - \left(\frac{C_{\text{Sector}, t+k}}{C_{\text{Sector}, t}} - 1\right)$
4. **Cross-Sectional Rank Target**: $R_{\text{rank}} = \text{Rank}\left(R_{\text{raw}, i}\right) / N$

---

## 3. Evaluation Criteria

The primary target horizon will be selected based on:
- **Spearman Rank IC**: Cross-sectional correlation between signal score and forward return.
- **Deflated Sharpe Ratio**: Significance adjusted for multiple tested horizons.
- **Friction Break-Even**: Net alpha after accounting for 2x multi-day round-trip spread/slippage friction (~5.0 bps).
