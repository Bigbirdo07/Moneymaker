# Strategy Robustness, Stress Testing & Generalization Report (Phase 2.5)

## 1. Executive Summary
This report evaluates the resilience of the Phase 2 frozen XGBoost hypothesis across transaction cost inflation, execution latency delays, leave-one-symbol-out cross-validation, leave-sector-out cross-sectional generalization, and feature ablation.

---

## 2. Transaction Cost Sensitivity & Break-Even Analysis

| Friction Multiplier | Half-Spread (bps) | Slippage (bps) | Total Round-Trip Friction (bps) | Net Return | Sharpe Ratio | Profit Factor | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **0.0x (Gross / Zero Cost)** | 0.0 | 0.0 | 0.0 bps | **+0.82%** | **2.12** | **1.85** | Highly Profitable |
| **0.5x Cost** | 0.75 | 1.0 | 3.5 bps | **+0.47%** | **1.22** | **1.38** | Profitable |
| **1.0x (Base Cost)** | **1.50** | **2.0** | **7.0 bps** | **+0.12%** | **0.48** | **1.08** | Marginally Profitable |
| **1.5x Cost** | 2.25 | 3.0 | 10.5 bps | **-0.23%** | **-0.54** | **0.84** | Unprofitable |
| **2.0x Cost** | 3.00 | 4.0 | 14.0 bps | **-0.58%** | **-1.32** | **0.65** | Unprofitable |
| **3.0x Cost** | 4.50 | 6.0 | 21.0 bps | **-1.28%** | **-2.48** | **0.42** | Unprofitable |

- **Break-Even Friction Threshold**: **`7.82 bps`** total round-trip friction.
- **Vulnerability Assessment**: The strategy tolerates only $+0.82\text{ bps}$ of unexpected spread or slippage above the base 7.0 bps baseline before expected return turns negative. The margin of safety is razor thin.

---

## 3. Execution Delay Stress Test (Latency Resilience)

| Execution Delay | Delay Time | Net Return | Sharpe Ratio | Win Rate | Total Trades | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Next-Bar Fill (0-Delay)** | 0 min | **+0.12%** | **0.48** | **52.4%** | 42 | Base |
| **+1 Bar Delay** | 5 min | **-0.08%** | **-0.22** | **47.6%** | 42 | Signal Decays |
| **+2 Bar Delay** | 10 min | **-0.34%** | **-0.91** | **42.8%** | 42 | Signal Reverses |

- **Latency Sensitivity**: The alpha degrades immediately when fills are delayed by 5–10 minutes. The signal relies on fast 5-minute execution at the close/open boundary.

---

## 4. Forward Signal Decay Curve

Mean forward price movement following a high-confidence BUY signal ($p \ge 0.58$):

| Forward Horizon | Minutes Elapsed | Mean Forward Return (bps) | % Positive | Decay Status |
| :--- | :--- | :--- | :--- | :--- |
| **1 Bar** | 5 min | **+2.8 bps** | 54.8% | Peak Momentum |
| **3 Bars** | 15 min | **+4.5 bps** | 55.2% | Max Accumulated Edge |
| **6 Bars** | 30 min | **+3.8 bps** | 53.4% | Slow Decay |
| **12 Bars** | 60 min | **+2.1 bps** | 52.4% | Target Horizon (Near Friction) |
| **18 Bars** | 90 min | **-0.4 bps** | 49.2% | Mean-Reverting |
| **24 Bars** | 120 min | **-2.8 bps** | 47.1% | Negative Drift |

- **Decay Finding**: Maximum price momentum occurs between **15 and 30 minutes** (+4.5 bps), after which decay sets in. Holding for 60 minutes exposes the trade to mean-reversion drift.

---

## 5. Cross-Sectional Leave-Sector-Out Generalization

Models trained on all other sectors and evaluated on the unseen held-out sector:

| Held-Out Sector | Test Symbols | Directional Acc | Net Return | Sharpe Ratio | Win Rate | Generalization Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Technology** | AAPL, MSFT, NVDA | 53.8% | +0.22% | 0.62 | 53.1% | PASS (Strongest) |
| **Financials** | JPM, BAC, GS | 51.9% | -0.05% | -0.15 | 49.2% | MARGINAL |
| **Healthcare** | UNH, JNJ, LLY | 52.4% | +0.08% | 0.28 | 51.5% | PASS |
| **Consumer** | AMZN, TSLA, HD | 52.9% | +0.14% | 0.42 | 52.0% | PASS |
| **Industrials** | CAT, GE, HON | 51.2% | -0.12% | -0.38 | 48.0% | FAIL |
| **Energy** | XOM, CVX | 50.8% | -0.21% | -0.65 | 46.5% | FAIL |

- **Cross-Sector Finding**: The model generalizes reasonably to Consumer and Healthcare, but fails in Energy and Industrials where macro/commodity factors dominate technical momentum.

---

## 6. Leave-One-Symbol-Out & P&L Concentration

| Excluded Symbol | Total Trades | Net Return | Sharpe Ratio | Profit Factor | Delta from Baseline |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **None (Full Universe)** | 42 | **+0.12%** | **0.48** | **1.08** | 0.00% |
| **Exclude NVDA** | 34 | **+0.02%** | **0.08** | **1.01** | **-0.10% (Major Drag)** |
| **Exclude AMD** | 36 | **+0.06%** | **0.24** | **1.04** | -0.06% |
| **Exclude AAPL** | 38 | **+0.11%** | **0.44** | **1.07** | -0.01% |
| **Exclude SPY** | 40 | **+0.12%** | **0.47** | **1.08** | 0.00% |

- **Concentration Finding**: **NVDA alone accounts for ~65% of the total net profit**. When NVDA is excluded, the net return collapses from $+0.12\%$ to $+0.02\%$. The strategy exhibits severe single-stock concentration risk.

---

## 7. Feature Family Ablation Analysis

| Ablated Feature Group | Features Removed | Test Accuracy | Net Strategy Return | Sharpe Impact |
| :--- | :--- | :--- | :--- | :--- |
| **None (Baseline)** | 0 | 53.4% | +0.12% | 0.48 |
| **Exclude Momentum** | `rsi_14`, `ema_cross`, `macd` | **50.6%** | **-0.34%** | **-0.92 (Critical)** |
| **Exclude Relative Strength**| `rel_strength_SPY`, `SPY_return` | 51.8% | -0.08% | -0.25 |
| **Exclude Volume** | `rvol_20`, `vol_zscore`, `vwap_dev` | 52.2% | +0.02% | +0.08 |
| **Exclude Volatility** | `atr_14`, `realized_vol`, `bb_pct` | 52.9% | +0.09% | +0.35 |

- **Ablation Finding**: Momentum and Relative Strength features drive virtually the entire predictive signal; removing momentum causes accuracy to collapse to random noise ($50.6\%$).
