# Survivorship Bias & Listing History Audit (Phase B)

## 1. Audit Overview
Evaluating a historical strategy against today's current S&P 500 or Nasdaq 100 components retroactively introduces **survivorship bias**—artificially inflating backtest returns by excluding companies that suffered distress, delisting, or bankruptcy in past years.

---

## 2. Empirical Methodology & Mitigation

| Bias Risk | Mechanism | Mitigation in Moneymaker Architecture |
| :--- | :--- | :--- |
| **Survivor Selection Bias** | Filtering 2021 history by 2026 active tickers | Point-in-time exchange listings evaluated daily at session open. |
| **IPO Lookahead Bias** | Backtesting newly listed stocks prior to their IPO | Strict minimum 60-trading-day history requirement before qualification. |
| **Delisting Drop Bias** | Dropping bankrupt / acquired names | Symbols delisted mid-year are retained in history with actual final exit prices. |
| **Corporate Action Discontinuities** | Unadjusted splits or special dividends | Verified against split calendar with continuous volume-weighted price continuity. |

---

## 3. Provenance Assertion
All Phase B experiments utilize historical listing metadata and point-in-time rolling 30-day volume windows, ensuring zero survivorship or future-membership leakage.
