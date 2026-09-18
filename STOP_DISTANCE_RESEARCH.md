# Effective Stop Distance Research

## 1. Dynamic Stop Distance Modeling
- Fixed percentage stops fail across stocks with differing beta.
- Effective stop distance is formulated as: $\text{Effective Stop} = \max(1.0\%, 1.5 \times \text{Realized Intraday Volatility}, \text{MAE Quantile})$.
- Clamped between a **1.0% floor** and a **3.5% ceiling**.