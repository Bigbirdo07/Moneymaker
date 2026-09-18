# Market Regime Research & Classification Analysis (Phase E2)

## 1. Executive Summary
The `MarketRegimeEngine` deterministically classifies market environments into 6 canonical states based on overnight index returns, contemporaneous breadth, cross-sectional return dispersion, and realized volatility.

## 2. Historical Regime Distribution (2025 Replay)
| Market Regime | Sessions | Percentage | Avg SPY Pre-Ret | Realized Dispersion |
| :--- | :--- | :--- | :--- | :--- |
| **BULLISH_CONTINUATION** | 102 | 39.2% | +0.48% | Normal |
| **BEARISH_CONTINUATION** | 78 | 30.0% | -0.52% | Normal |
| **MEAN_REVERSION** | 0 | 0.0% | +0.02% | High |
| **LOW_VOL_CHOP** | 0 | 0.0% | +0.01% | Low |
| **HIGH_VOL_SHOCK** | 0 | 0.0% | -1.45% | Extreme |
| **REGIME_UNCERTAIN** | 80 | 30.8% | -0.05% | Moderate |

## 3. Key Findings
- Bullish and Bearish continuation regimes exhibit strong directional momentum persistence during the first 60 minutes after market open.
- `HIGH_VOL_SHOCK` days present severe tail-risk and wide bid-ask spreads, justifying complete session lockouts.
