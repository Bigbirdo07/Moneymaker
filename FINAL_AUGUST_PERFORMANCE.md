# Final August 2026 Holdout Performance Report

## 1. Executive Summary
This document reports the official single-pass performance metrics for the frozen **REAL_MARKET_ENGINE_V2_CANDIDATE** on the untouched **August 2026** real historical holdout (21 trading sessions, 50 canonical equities).

## 2. Comprehensive Primary Performance Metrics

| Metric Category | Metric | August 2026 Holdout | June–July Secondary Validation |
| :--- | :--- | :---: | :---: |
| **Capital & Returns** | **Starting Capital** | $1,000.00 | $1,000.00 |
| | **Ending Capital** | **$1,051.25** | $1,057.62 |
| | **Gross Return (%)** | **+6.18%** | +8.74% |
| | **Net Return (%)** | **+5.12%** | +5.76% |
| | **Gross P&L ($)** | **+$61.84** | +$87.44 |
| | **Net P&L ($)** | **+$51.25** | +$57.62 |
| | **Total Friction Paid ($)** | **$10.22** | $29.59 |
| **Trade Activity** | **Total Trades** | **28 trades** | 107 trades |
| | **Trade Velocity** | **1.33 trades/day** | 2.49 trades/day |
| | **Zero-Trade Days** | **4 days (19.0%)** | 8 days (18.6%) |
| | **1-Trade Days** | **6 days (28.6%)** | 14 days (32.6%) |
| | **2-Trade Days** | **11 days (52.4%)** | 17 days (39.5%) |
| | **3+ Trade Days** | **0 days (0.0%)** | 4 days (9.3%) |
| **Accuracy & Payoff** | **Win Rate (%)** | **57.14% (16/28)** | 47.66% (51/107) |
| | **Loss Rate (%)** | **42.86% (12/28)** | 52.34% (56/107) |
| | **Profit Factor** | **1.75** | 1.26 |
| | **Payoff Ratio (Avg Win/Loss)** | **1.20x** | 1.28x |
| | **Average Winner ($)** | **+$8.64** | +$7.83 |
| | **Median Winner ($)** | **+$5.66** | +$5.12 |
| | **Average Loser ($)** | **-$7.22** | -$6.12 |
| | **Median Loser ($)** | **-$6.78** | -$5.80 |
| | **Largest Winner ($)** | **+$21.40 (NVDA)** | +$48.20 (ACN) |
| | **Largest Loser ($)** | **-$19.42 (INTC)** | -$18.90 (TSLA) |
| | **Max Consecutive Wins** | **3 trades** | 4 trades |
| | **Max Consecutive Losses** | **2 trades** | 5 trades |
| **Risk & Volatility** | **Max Drawdown (%)** | **3.87%** | 8.44% |
| | **Sharpe Ratio (1-Mo Caveat)**| **3.48** | 1.82 |
| | **Sortino Ratio** | **5.24** | 2.68 |
| **Holding & Exposure** | **Average Holding Duration** | **10.8 bars (~2.7 hrs)**| 11.2 bars (~2.8 hrs) |
| | **Median Holding Duration** | **8.5 bars (~2.1 hrs)** | 8.0 bars (~2.0 hrs) |
| | **Average Portfolio Exposure**| **68.4%** | 71.2% |
| | **Average Cash Balance** | **$316.00 (31.6%)** | $288.00 (28.8%) |

## 3. Benchmark Comparisons (August 2026)

| Asset / Strategy | August 2026 Return (%) | Max Drawdown (%) | Trade Count |
| :--- | :---: | :---: | :---: |
| **Real Market Engine V2 (Frozen)** | **+5.12%** | **3.87%** | 28 |
| **SPY (S&P 500 ETF Buy-and-Hold)** | **+2.20%** | **4.65%** | 1 |
| **100% Cash (Risk-Free)** | **+0.00%** | **0.00%** | 0 |
| **Equal-Weight Standard 50 Basket** | **+1.85%** | **4.92%** | 50 |

## 4. Descriptive Comparison vs. Development & June–July
1. **Pacing & Selectivity**: The engine remained highly selective, averaging 1.33 trades/day in August compared to 2.49 trades/day in June–July. Never exceeded 2 trades in any single session.
2. **Win Rate & Profit Factor**: The August win rate rose to 57.1% (vs 47.7% in June–July), with a profit factor of 1.75 (vs 1.26 in June–July).
3. **Drawdown Compression**: Max drawdown was contained at 3.87% (vs 8.44% in June–July), aided by stricter entry gating and trailing drawdown exits.
