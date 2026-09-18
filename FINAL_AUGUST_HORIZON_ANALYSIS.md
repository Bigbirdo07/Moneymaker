# Final August 2026 Holdout Horizon Consistency Report

## 1. Overview & Objective
This report evaluates the performance of the frozen **REAL_MARKET_ENGINE_V2_CANDIDATE** across prediction and holding horizons (15m, 30m, 60m, and actual realized holding duration) during the untouched August 2026 holdout.

## 2. Target Horizon Trade Performance

| Target Horizon | Sample Count | Win Count | Win Rate (%) | Gross P&L ($) | Friction ($) | Net P&L ($) | Net Expectancy / Trade ($) | Profit Factor | Avg Bars Held | Median Bars Held |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **15m Horizon** | 0 | 0 | N/A | $0.00 | $0.00 | $0.00 | $0.00 | N/A | N/A | N/A |
| **30m Horizon** | 4 | 2 | 50.0% | +$14.14 | $1.46 | +$12.68 | +$3.17 | 4.15 | 11.0 | 11.0 |
| **60m Horizon** | 24 | 14 | 58.3% | +$47.70 | $8.77 | +$38.93 | +$1.62 | 1.47 | 10.8 | 8.5 |
| **Total Holdout** | **28** | **16** | **57.1%** | **+$61.84** | **$10.22** | **+$51.25** | **+$1.84** | **1.75** | **10.8** | **8.5** |

## 3. Realized Holding Duration Distribution

| Quantile | Holding Time (15-min Bars) | Equivalent Real Time (Minutes) |
| :--- | :---: | :---: |
| **Min (0%)** | 1 bar | 15 minutes |
| **10th Percentile** | 2.4 bars | 36 minutes |
| **25th Percentile** | 3.75 bars | 56 minutes |
| **Median (50%)** | 8.5 bars | 128 minutes (~2.1 hours) |
| **75th Percentile** | 15.25 bars | 229 minutes (~3.8 hours) |
| **90th Percentile** | 24.3 bars | 365 minutes (~6.1 hours) |
| **Max (100%)** | 27 bars | 405 minutes (~6.8 hours / multi-session) |

## 4. Key Findings & Horizon Insights
1. **Dominance of 60m Entry Target**: 85.7% (24 of 28) of authorized trades were classified under the 60-minute target horizon. The higher gross expected alpha on the 60m horizon allowed candidates to reliably clear the 12.0 bps entry threshold net of estimated friction.
2. **Realized Holding Extension**: While target horizons are 30m and 60m, dynamic trailing stops and multi-session holding logic allowed winning positions (e.g. NVDA, ORCL, ACN) to run across 10–27 bars (150–405 minutes), capturing substantial multi-percent trend moves (+3.0% to +5.15% take-profit targets).
3. **No 15m Trades**: 15m signals failed to clear the entry gating hurdle (12 bps required edge), properly preventing excessive churning in noise.
