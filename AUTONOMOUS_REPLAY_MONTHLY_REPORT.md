# Autonomous Historical Market Replay Monthly Report

## 1. Executive Summary
- **Simulated Capital Range**: $1,000.00 $\to$ $897.76 USD (-10.22% net return).
- **Universe**: 50 liquid U.S. equities (1-minute resolution, 22 trading sessions).
- **Total Trades Executed**: 658 round-trip trades.
- **Total Friction Incurred**: $43.00 (Spread: $26.42, Slippage: $14.86, Commissions: $1.72).
- **Leakage Integrity**: 91,018 clock assertions verified with **0 violations**.

---

## 2. Comprehensive Monthly Performance Telemetry

| Metric | Measured Value | Benchmark (100% Cash) | Benchmark (SPY B&H) |
| :--- | :--- | :--- | :--- |
| **Starting Capital** | $1,000.00 | $1,000.00 | $1,000.00 |
| **Ending Capital** | $897.76 | $1,000.00 | $1,014.20 |
| **Gross Return** | -5.92% | 0.00% | +1.42% |
| **Net Return** | -10.22% | 0.00% | +1.42% |
| **Total Net P&L** | -$102.24 | $0.00 | +$14.20 |
| **Total Friction Paid** | $43.00 | $0.00 | $0.20 |
| **Total Trades** | 658 | 0 | 1 |
| **Win Rate** | 32.1% (211/658) | N/A | 100% |
| **Average Winner** | +$0.58 | N/A | +$14.20 |
| **Average Loser** | -$0.50 | N/A | N/A |
| **Profit Factor** | 0.65 | N/A | N/A |
| **Sharpe Ratio** | -13.22 | 0.00 | +1.45 |
| **Sortino Ratio** | -18.67 | 0.00 | +2.10 |
| **Max Intraday Drawdown** | 11.4% | 0.00% | 3.2% |
| **Average Cash Utilization** | 31.4% | 0.00% | 100.0% |

---

## 3. Decision Regret & Quality Attribution
- **Entry Quality**:
  - `GOOD_ENTRY`: 231 (35.1%)
  - `LOW_EDGE_ENTRY`: 218 (33.1%)
  - `LATE_ENTRY`: 114 (17.3%)
  - `FALSE_POSITIVE`: 95 (14.4%)
- **Exit Quality**:
  - `SESSION_CLOSE`: 284 (43.2%)
  - `SIGNAL_DECAY`: 142 (21.6%)
  - `STOP_LOSS`: 98 (14.9%)
  - `DRAWDOWN_FROM_PEAK`: 62 (9.4%)
  - `TAKE_PROFIT`: 41 (6.2%)
  - `BETTER_OPPORTUNITY`: 21 (3.2%)
  - `TIME_STOP`: 10 (1.5%)

---

## 4. Market Regime Breakdown

| Regime | Session Count | Win Rate | Net Return (%) | Friction Paid ($) |
| :--- | :--- | :--- | :--- | :--- |
| **Bullish Trend Days** | 6 | 45.8% | +1.84% | $11.20 |
| **Bearish Trend Days** | 5 | 24.2% | -5.60% | $10.10 |
| **High Volatility Days** | 4 | 22.8% | -4.80% | $9.80 |
| **Low Volatility Sideways** | 7 | 34.5% | -1.66% | $11.90 |

---

## 5. Architectural Contributions & Ablations
1. **Without Exit Model (Fixed 15m Hold)**: Net Return drops to **-18.40%** (frictional churn doubles).
2. **Without Opportunity Re-Ranking**: Turnover decreases, but win rate degrades by 4.8%.
3. **Without Capital Allocator Bounds**: Max drawdown increases from 11.4% to 28.5%.
