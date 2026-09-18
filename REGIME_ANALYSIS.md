# Market Regime Performance & Volatility Analysis Report

## 1. Executive Summary

This report evaluates Autonomous Engine V1.0 performance across four macroeconomic and intraday market regimes: **High Volatility**, **Trending Bull**, **Trending Bear**, and **Range-Bound Chop**.

---

## 2. Regime Performance Breakdown

| Regime | Definition Criteria | Time in Regime (%) | Trade Count | Win Rate (%) | Gross P&L ($) | Friction ($) | Net P&L ($) | Return Contribution (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **High Volatility** | Realized 30m Vol > 2.0x 20-day mean | 22.4% | 242 | 26.8% | -$38.50 | $15.80 | -$54.30 | -5.43% |
| **Trending Bull** | 15m MACD > 0 & 30m Return > +15 bps | 31.8% | 184 | 39.1% | +$3.60 | $12.00 | -$8.40 | -0.84% |
| **Trending Bear** | 15m MACD < 0 & 30m Return < -15 bps | 18.2% | 112 | 29.5% | -$17.50 | $7.30 | -$24.80 | -2.48% |
| **Range-Bound Chop** | Realized Vol < 0.8x & ADX < 20 | 27.6% | 120 | 31.7% | -$6.84 | $7.90 | -$14.74 | -1.47% |
| **Total Strategy** | **All Regimes** | **100.0%** | **658** | **32.4%** | **-$59.24** | **$43.00** | **-$102.24** | **-10.22%** |

```
Net Loss by Regime ($):
High Volatility    ██████████████████████████ (-$54.30, 53.1% of all losses)
Trending Bear      ████████████ (-$24.80, 24.3% of all losses)
Range-Bound Chop   ███████ (-$14.74, 14.4% of all losses)
Trending Bull      ████ (-$8.40, 8.2% of all losses)
```

---

## 3. Key Findings

### 1. High Volatility Regime is the Primary Loss Vector:
- **53.1% of total strategy losses** (-$54.30) occurred during high-volatility periods.
- In elevated volatility, wider bid-ask spreads and sudden intraday mean-reversion triggered frequent `STOP_LOSS` and `SIGNAL_DECAY` exits before trend continuation.

### 2. Long-Only Bias in Trending Bear Regimes:
- Because the initial V1.0 execution was configured for long-only equities, bearish trend days suffered continuous long attempts into falling knives.

### 3. Trending Bull Generates Positive Gross Alpha:
- In trending bull regimes, the model produced **+$3.60 in gross profit** (39.1% win rate), but friction of $12.00 turned the net result negative (-$8.40).

---

## 4. Regime Guardrails for Engine V1.1

1. **Volatility Filter**: Scale minimum net edge dynamically in high volatility (require $\ge 15.0\text{ bps}$ when volatility is $> 2.0\sigma$).
2. **Trend Filter**: Reject long entries when intraday broad market index (SPY proxy) is down $> 1.0\%$ on the session.
3. **Cash Preservation in Hostile Regimes**: Engine V1.1 remains 100% in CASH when market regime volatility exceeds risk limits.
