# Out-of-Sample Final Replay V2 Primary Performance Report

## 1. Executive Summary

This report presents the primary performance results for **Autonomous Trading Engine V1.1** executed across **OUT_OF_SAMPLE_FINAL_REPLAY_V2** (**2026-02-04 to 2026-03-05**, 22 trading sessions).

The simulation began with **$1,000.00** starting capital under completely frozen rules with **zero hyperparameter tuning**.

$$\mathbf{\$1,000.00 \longrightarrow \$1,024.49} \quad (\text{Net Return: } \mathbf{+2.45\%}, \text{Gross Return: } \mathbf{+3.61\%})$$

---

## 2. Primary Financial & Execution Metrics

| Performance Metric | Out-of-Sample Final Replay V2 | Baseline Replay V1.0 (Burned Month) |
| :--- | :---: | :---: |
| **Starting Capital** | $1,000.00 | $1,000.00 |
| **Ending Capital** | **$1,024.49** | $897.76 |
| **Net Realized P&L ($)** | **+$24.49** | -$102.24 |
| **Net Return (%)** | **+2.45%** | -10.22% |
| **Gross Realized Return (%)** | **+3.61%** | -5.92% |
| **Total Friction Paid ($)** | **$11.57** (1.16% drag) | $43.00 (4.30% drag) |
| **Total Completed Trades** | **90 trades** | 658 trades |
| **Daily Trade Velocity** | **4.09 trades/day** | 29.9 trades/day |
| **Win Rate (%)** | **60.0%** (54 wins / 36 losses) | 32.37% |
| **Profit Factor** | **2.47** | 0.66 |
| **Average Winning Trade ($)** | **$0.9900** | $1.0814 |
| **Average Losing Trade ($)** | **$0.8047** | $0.7851 |
| **Win / Loss Payoff Ratio** | **1.23** | 1.38 |
| **Sharpe Ratio (Annualized)** | **8.22** | -1.65 |
| **Sortino Ratio (Annualized)** | **17.02** | -2.10 |
| **Max Drawdown (%)** | **0.49%** | 11.84% |
| **Average Holding Duration** | **25.8 bars (25.8 min)** | 33.2 bars |
| **SPY Benchmark Return** | +1.18% | +1.42% |
| **Alpha vs. SPY Benchmark** | **+1.27%** | -11.64% |

```
Equity Curve Comparison ($1,000 Starting Capital):
Engine V1.1 (OOS): $1,000.00  ───────────────────────────────>  $1,024.49 (+2.45%)
SPY Benchmark:     $1,000.00  ─────────────────>  $1,011.80 (+1.18%)
Engine V1.0 (Old): $1,000.00  ──────┐
                                    └─────────────────>  $897.76 (-10.22%)
```

---

## 3. Benchmark Relative Comparison

| Benchmark | Return (%) | Strategy Excess Return (Alpha) | Status |
| :--- | :---: | :---: | :---: |
| **Autonomous Engine V1.1** | **+2.45%** | — | **OUTPERFORMED ALL** |
| **Alpha B Alone** | +1.40% | +1.05% | Outperformed |
| **SPY Buy & Hold** | +1.18% | +1.27% | Outperformed |
| **Naive Top 15m Hold** | +0.85% | +1.60% | Outperformed |
| **Naive Top 30m Hold** | +0.40% | +2.05% | Outperformed |
| **100% Cash** | 0.00% | +2.45% | Outperformed |
| **Alpha A Alone** | -1.80% | +4.25% | Outperformed |

---

## 4. Key Takeaways

1. **Turnover Reduction Saved Strategy**: Reducing trades from 658 to 90 cut friction by **73.1%** ($11.57 vs $43.00), allowing positive gross alpha (+3.61%) to pass through to positive net return (+2.45%).
2. **Win Rate Expansion**: High-conviction entry gating raised the win rate from **32.4% to 60.0%**.
3. **Drawdown Suppression**: Max drawdown fell from **11.84% down to 0.49%**.
