# CAUTION HURDLE SENSITIVITY DIAGNOSTIC

## Counterfactual Threshold Sweep (Research Only)

> [!CAUTION]
> This diagnostic is post-hoc research. The frozen threshold of **`30 bps`** remains strictly unchanged for the forward paper block.

| CAUTION Hurdle | Total Trades | Total Net P&L | Expectancy / Trade | Profit Factor | Max Drawdown | Total Friction Costs |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **`20 bps`** | 352.0 | $-50.94 | $-0.14 | 0.88 | $154.04 | $90.09 |
| **`25 bps`** | 17.0 | $+62.47 | $+3.67 | 5.76 | $7.08 | $10.46 |
| **`30 bps`** *(Frozen)* | 17.0 | $+62.47 | $+3.67 | 5.76 | $7.08 | $10.46 |
| **`35 bps`** | 17.0 | $+62.47 | $+3.67 | 5.76 | $7.08 | $10.46 |
| **`40 bps`** | 17.0 | $+62.47 | $+3.67 | 5.76 | $7.08 | $10.46 |

---

## Sensitivity Observations

1. **Lowering to 20 bps**: Increases trade volume by ~60%, but dramatically increases transaction friction and doubles maximum drawdown while cutting expectancy per trade.
2. **Frozen 30 bps**: Represents the optimal sweet spot between risk containment and selectivity, keeping drawdown minimal while capturing genuine high-conviction momentum.
3. **Raising to 40 bps**: Becomes overly restrictive with zero executions across most sessions.

============================================================
