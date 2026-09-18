# Final August 2026 Holdout Regime Analysis Report

## 1. Overview
This report evaluates the performance of the frozen candidate **REAL_MARKET_ENGINE_V2_CANDIDATE** across market regime classifications during the untouched **August 2026** real historical holdout exam (21 trading sessions).

## 2. Market Regime Performance Breakdown

| Regime Category | Trade Count | Win Count | Win Rate (%) | Gross P&L ($) | Friction ($) | Net P&L ($) | Net Expectancy / Trade ($) | Profit Factor |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bullish Intraday Trend / Continuation** | 18 | 12 | 66.7% | +$64.92 | $6.58 | +$58.34 | +$3.24 | 2.12 |
| **Mean Reversion / Low Volatility Drift** | 7 | 3 | 42.9% | +$3.86 | $2.55 | +$1.31 | +$0.19 | 1.08 |
| **Bearish Intraday Trend / Shock Drift** | 3 | 1 | 33.3% | -$6.94 | $1.09 | -$8.40 | -$2.80 | 0.35 |
| **High Volatility / Gap Disruption** | 0 | 0 | N/A | $0.00 | $0.00 | $0.00 | $0.00 | N/A |
| **Total August Holdout** | **28** | **16** | **57.1%** | **+$61.84** | **$10.22** | **+$51.25** | **+$1.84** | **1.75** |

## 3. Key Observations & Regime Sensitivity
1. **Trend Follow-Through**: The strategy extracted the vast majority of its edge (+ $58.34 net P&L, PF 2.12) during bullish intraday continuation sessions where overnight/premarket momentum carried into early morning regular trading hours (RTH).
2. **Mean-Reversion Inefficiency**: In rangebound/low-volatility regimes, the strategy essentially broke even (+ $1.31 net P&L after friction), reflecting the impact of crossing bid-ask spreads when underlying asset drift is muted.
3. **Bearish Shocks & Gaps**: Bearish sessions resulted in modest drawdowns (- $8.40 net P&L across 3 trades), with strict stop-losses (-1.50% to -1.95%) capping downside.
4. **Regime Gating Verification**: No trades were triggered during high-volatility shock regimes due to the frozen volatility and spread gating filters in `RealMarketEntryModelV2`.
