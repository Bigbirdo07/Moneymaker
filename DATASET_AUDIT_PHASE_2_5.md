# Dataset Integrity & Quality Audit (Phase 2.5)

## 1. Data Provider & Ingestion Architecture
- **Provider Interface**: [`HistoricalMarketDataProvider`](file:///Users/albertopaz/Moneymaker/src/data/provider.py) abstract provider architecture with local Parquet caching.
- **Bar Resolution**: 5-Minute Intraday Bars.
- **Session Times**: Regular US Equity Hours (09:30:00 to 16:00:00 ET), converted and normalized internally to UTC.

---

## 2. Universe Coverage & Sector Composition
Total active universe: **36 Liquid US Equities & Benchmark ETFs**

| Sector | ETF | Active Ticker Symbols |
| :--- | :--- | :--- |
| **Broad Market** | SPY | SPY, QQQ, IWM |
| **Technology** | XLK | AAPL, MSFT, NVDA, AMD, AVGO, ORCL, CSCO, INTC |
| **Communication Services** | XLC | GOOGL, META, NFLX, DIS |
| **Consumer Discretionary** | XLY | AMZN, TSLA, HD, NKE, MCD |
| **Consumer Staples** | XLP | PG, KO, PEP, COST, WMT |
| **Financials** | XLF | JPM, BAC, GS, MS, WFC |
| **Healthcare** | XLV | UNH, JNJ, LLY, ABBV, MRK, PFE |
| **Industrials** | XLI | CAT, GE, HON, BA, UPS |
| **Energy** | XLE | XOM, CVX, SLB, COP |

---

## 3. Data Quality & Anomaly Scans

Across all ingested historical bars, the [`DataValidator`](file:///Users/albertopaz/Moneymaker/src/data/validation.py) audited:
1. **Missing Timestamps**: Regular session gaps between 16:00 and 09:30 are session-aware and isolated.
2. **Duplicate Timestamps**: Zero duplicate timestamps allowed.
3. **Out-of-Order Rows**: Monotonic timestamp ordering strictly enforced.
4. **Impossible OHLC Bounds**: Verified $\text{High} \ge \text{Low}$, $\text{Open}, \text{Close} \in [\text{Low}, \text{High}]$ for 100% of observations.
5. **Negative Volume**: Zero negative volume bars detected.
6. **Extreme Gaps**: Monitored single-bar price moves $>20\%$.

---

## 4. Corporate Action & Split Safety Audit
- **Split Management** ([`src/data/corporate_actions.py`](file:///Users/albertopaz/Moneymaker/src/data/corporate_actions.py)): Automated detection of unadjusted split jumps (e.g. 50% overnight drops with $2\times$ volume).
- **Backward Adjustment**: Applied cumulative ratio adjustments to historical Open, High, Low, Close, and inverse adjustment to Volume to ensure historical indicators (e.g. 50-period SMA, ATR) do not produce artificial breakout signals on split execution dates.

---

## 5. Known Limitations & Survivorship Bias
1. **Current Universe Selection**: The 36 universe symbols are large-cap companies that are currently liquid. Testing historical periods with today's liquid universe introduces survivorship bias.
2. **Execution Reality**: Real tick-by-tick order books may experience queue delays during opening (09:30–09:45 ET) that 5-minute discrete bars cannot fully reflect.
