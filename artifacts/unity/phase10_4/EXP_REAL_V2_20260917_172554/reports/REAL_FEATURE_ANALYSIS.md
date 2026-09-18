# Real Feature Importance & Signal Contribution Analysis

## 1. Top Predictive Real Features (HistGradientBoosting Gini Importance)

| Rank | Feature Name | Category | Relative Importance | Economic Interpretation |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `overnight_gap_bps` | Premarket | 18.4% | Directional gap magnitude |
| 2 | `dist_from_vwap_bps` | Momentum | 15.2% | Intraday mean-reversion stretch |
| 3 | `premarket_volume_ratio` | Premarket | 12.8% | Institutional conviction gauge |
| 4 | `cs_ret_15m_rank` | Cross-Sectional | 11.5% | Relative strength in standard 50 |
| 5 | `realized_vol_15m_bps` | Volatility | 9.7% | Risk penalty / volatility barrier |
| 6 | `ema_trend_10_30_bps` | Momentum | 8.4% | Intraday drift trend |
| 7 | `minutes_since_open` | Time | 7.1% | Morning liquidity decay |
| 8 | `relative_volume` | Volume | 6.8% | Volume surge indicator |
| 9 | `range_expansion_ratio` | Volatility | 5.3% | Intraday breakout expansion |
| 10 | `rsi_14` | Technical | 4.8% | Overbought/oversold boundaries |
