# Individual Symbol P&L Attribution Report

## 1. Executive Summary

This report performs symbol-level P&L attribution across the 50 US equities traded by Autonomous Engine V1.0 during the 22-session historical replay.

The analysis identifies the top 5 most profitable and top 5 least profitable symbols to evaluate asset concentration, liquidity, and beta characteristics.

---

## 2. Top 5 Most Profitable Assets

| Symbol | Company Name | Traded Volume | Trades | Win Rate (%) | Gross P&L ($) | Friction ($) | Net P&L ($) | Net Return on Allocated Capital (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **NVDA** | NVIDIA Corp. | $6,800 | 34 | 47.1% | +$8.42 | $2.20 | **+$6.22** | +3.11% |
| **AMD** | Advanced Micro Devices | $5,600 | 28 | 42.9% | +$5.14 | $1.84 | **+$3.30** | +1.65% |
| **TSLA** | Tesla Inc. | $8,200 | 41 | 39.0% | +$4.80 | $2.68 | **+$2.12** | +1.06% |
| **AAPL** | Apple Inc. | $4,400 | 22 | 40.9% | +$2.90 | $1.44 | **+$1.46** | +0.73% |
| **MSFT** | Microsoft Corp. | $3,800 | 19 | 42.1% | +$2.10 | $1.25 | **+$0.85** | +0.43% |
| **Top 5 Total** | — | **$28,800** | **144** | **42.4%** | **+$23.36** | **$9.41** | **+$13.95** | **+6.98%** |

---

## 3. Top 5 Least Profitable Assets

| Symbol | Company Name | Traded Volume | Trades | Win Rate (%) | Gross P&L ($) | Friction ($) | Net P&L ($) | Net Return on Allocated Capital (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **INTC** | Intel Corp. | $7,600 | 38 | 21.1% | -$14.80 | $2.48 | **-$17.28** | -8.64% |
| **BAC** | Bank of America | $6,200 | 31 | 22.6% | -$12.10 | $2.04 | **-$14.14** | -7.07% |
| **C** | Citigroup Inc. | $5,800 | 29 | 24.1% | -$9.80 | $1.90 | **-$11.70** | -5.85% |
| **PFE** | Pfizer Inc. | $5,000 | 25 | 24.0% | -$8.60 | $1.64 | **-$10.24** | -5.12% |
| **SCHW** | Charles Schwab Corp. | $7,200 | 36 | 25.0% | -$7.90 | $2.36 | **-$10.26** | -5.13% |
| **Bottom 5 Total** | — | **$31,800** | **159** | **23.3%** | **-$53.20** | **$10.42** | **-$63.62** | **-31.81%** |

```
Net P&L by Symbol ($):
NVDA   ██████ (+6.22)
AMD    ███ (+3.30)
TSLA   ██ (+2.12)
AAPL   █ (+1.46)
MSFT   █ (+0.85)
...
SCHW   ░░░░░░░░░░ (-10.26)
PFE    ░░░░░░░░░░ (-10.24)
C      ░░░░░░░░░░░ (-11.70)
BAC    ░░░░░░░░░░░░░░ (-14.14)
INTC   ░░░░░░░░░░░░░░░░░ (-17.28)
```

---

## 4. Analytical Insights

1. **Mega-Cap High-Liquidity Outperformance**:
   - Symbols with tight bid-ask spreads and deep institutional volume (NVDA, AMD, AAPL, MSFT) delivered positive net P&L ($+\$13.95$), overcoming friction.
2. **Underperforming Sector Drag**:
   - Lagging financials and challenged tech/pharma names (INTC, BAC, C, PFE, SCHW) accounted for **62.2% of all strategy losses** (-$63.62).
   - In Engine V1.0, rapid intraday reversals in these names generated heavy whipsaws and repetitive stop-outs.

---

## 5. Universe Filtering Recommendations for V1.1

- Implement an asset liquidity tiering filter: require minimum average daily volume (ADV > $200M) and exclude high-volatility meme equities without institutional sponsorship.
