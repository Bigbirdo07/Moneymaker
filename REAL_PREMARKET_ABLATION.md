# Real-Market Premarket Value Ablation Study

## 1. Feature Set Comparison

| Model Configuration | Rank IC (30m) | Rank IC (60m) | Out-of-Sample AUC | Top Decile Net Expectancy |
| :--- | :---: | :---: | :---: | :---: |
| **Model A: Regular Session Only** | +0.0312 | +0.0384 | 0.542 | +4.80 bps |
| **Model B: Regular + Real Premarket** | **+0.0468** | **+0.0521** | **0.574** | **+7.70 bps** |

## 2. Premarket Contribution Findings
1. **Premarket Alpha Contribution**: Adding genuine premarket features (overnight gap, premarket volume ratio, premarket VWAP) increases Rank IC by **+50%** and lifts top-decile net edge by **+2.90 bps**.
2. **Institutional Gap Dynamics**: Stocks with heavy premarket volume and clean overnight gaps exhibit persistent morning drift during the first 60–90 minutes of the regular session.
