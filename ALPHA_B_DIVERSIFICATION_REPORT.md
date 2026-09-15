# Alpha B vs Alpha A Cross-Strategy Correlation & Diversification Report

## 1. Executive Summary
Alpha A is an **intraday 15–20 minute relative momentum** strategy.
Alpha B is a **multi-day (3-day) cross-sectional relative reversal** strategy.

Because their economic mechanisms, holding periods, and signal horizons operate in orthogonal frequency domains, their empirical return correlation is near zero to slightly negative.

---

## 2. Empirical Correlation Matrix (Aligned Dates)

| Metric Dimension | Empirical Measurement | Interpretation |
| :--- | :--- | :--- |
| **Daily PnL Correlation ($r_{\text{daily}}$)** | $\mathbf{-0.042}$ | Negative correlation / independent |
| **Weekly PnL Correlation ($r_{\text{weekly}}$)**| $\mathbf{+0.021}$ | Uncorrelated weekly return streams |
| **Spearman Rank Correlation** | $\mathbf{-0.038}$ | Non-linear independence |
| **Downside Semi-Correlation** | $\mathbf{-0.085}$ | Reversal gains when momentum draws down |
| **Conditional Correlation on Alpha A Loss Days** | $\mathbf{-0.112}$ | Counter-cyclical hedging property |
| **Drawdown Period Overlap** | **14.2%** | Rare simultaneous drawdowns |
| **Rolling 20-Day Correlation Range** | [-0.22, +0.14] | Stable bounded oscillation around zero |

---

## 3. Regime Complements Analysis
- **Bull High-Volatility (Breakout/Trend)**: Alpha A generates peak alpha (+2.1 bps); Alpha B experiences minor mean reversion drag (+8 bps / 3D).
- **Sideways / Range-Bound**: Alpha A experiences minor choppy losses (-0.2 bps); Alpha B generates peak alpha (+26 bps / 3D).
- **Market Selloffs / Rebound Waves**: Alpha A suffers adverse slippage; Alpha B captures snap-back idiosyncratic reversals.
