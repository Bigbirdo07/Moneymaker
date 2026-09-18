# Real Market Data Quality & Provenance Audit Report

## 1. Executive Summary
This report documents the empirical audit of the **6-month real historical 1-minute market dataset** ingested from the **Alpaca Stocks Historical Bars API (`ALPACA_IEX` feed)** across all 50 canonical `STANDARD_50_UNIVERSE` securities.

- **Provider**: Alpaca Markets
- **Market Feed**: `IEX` (`ALPACA_IEX`)
- **Date Range**: 2026-03-01 to 2026-09-02 (6 Complete Months)
- **Total Ingested Bars**: **2,227,357 bars**
- **Evidence Class**: `REAL_HISTORICAL_MARKET_DATA`
- **Synthetic Contamination**: **0.00% (Strictly Forbidden & Verified Zero)**

---

## 2. Symbol Audit Matrix

| Symbol | Bars Received | Invalid OHLC | Zero Volume | SHA-256 Hash Prefix | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **AAPL** | 50,960 | 0 | 0 | `b9e5e2f06556c97a...` | **SUCCESS** |
| **MSFT** | 50,640 | 0 | 0 | `2feb6edce0693364...` | **SUCCESS** |
| **NVDA** | 51,005 | 0 | 0 | `ff8e11d503c366ca...` | **SUCCESS** |
| **AMZN** | 50,144 | 0 | 0 | `de690a525125702e...` | **SUCCESS** |
| **GOOGL** | 50,212 | 0 | 0 | `8ab304c72b172329...` | **SUCCESS** |
| **META** | 49,807 | 0 | 0 | `568dba01c59ff840...` | **SUCCESS** |
| **TSLA** | 50,939 | 0 | 0 | `554d8d59e8e6a414...` | **SUCCESS** |
| **BRK.B** | 38,642 | 0 | 0 | `2dfaf7e7e3b2b1b5...` | **SUCCESS** |
| **UNH** | 46,086 | 0 | 0 | `c727b518dffaf8ad...` | **SUCCESS** |
| **JNJ** | 40,226 | 0 | 0 | `609a7dcfd61dfdd4...` | **SUCCESS** |
| **XOM** | 47,410 | 0 | 0 | `bbd0bfd9842f41c5...` | **SUCCESS** |
| **JPM** | 46,844 | 0 | 0 | `02f2fb71604a3ac2...` | **SUCCESS** |
| **V** | 48,154 | 0 | 0 | `352043edbecb0dd7...` | **SUCCESS** |
| **PG** | 43,843 | 0 | 0 | `d4dce837382aa208...` | **SUCCESS** |
| **MA** | 43,788 | 0 | 0 | `b8c3837e56f92d84...` | **SUCCESS** |
| **HD** | 43,679 | 0 | 0 | `f2568ff7b5371d0f...` | **SUCCESS** |
| **CVX** | 42,809 | 0 | 0 | `b394f161d0743cc7...` | **SUCCESS** |
| **ABBV** | 36,875 | 0 | 0 | `1b5b4dc6a9b90f44...` | **SUCCESS** |
| **MRK** | 42,742 | 0 | 0 | `bda80bfd9206b33c...` | **SUCCESS** |
| **COST** | 30,311 | 0 | 0 | `68a54eaa61bf8ff3...` | **SUCCESS** |
| **PEP** | 39,796 | 0 | 0 | `889efa01a72963a5...` | **SUCCESS** |
| **KO** | 49,307 | 0 | 0 | `62799f7419d7f42e...` | **SUCCESS** |
| **AVGO** | 50,464 | 0 | 0 | `3e4bf63c7d7f4413...` | **SUCCESS** |
| **ADBE** | 45,549 | 0 | 0 | `e901e828e9b60da6...` | **SUCCESS** |
| **WMT** | 49,284 | 0 | 0 | `a7122748f070fb81...` | **SUCCESS** |
| **CSCO** | 49,666 | 0 | 0 | `c7ad70f236dae209...` | **SUCCESS** |
| **MCD** | 43,401 | 0 | 0 | `8c654617576a9120...` | **SUCCESS** |
| **CRM** | 46,263 | 0 | 0 | `02e80fbb672072a2...` | **SUCCESS** |
| **BAC** | 49,686 | 0 | 0 | `79495e5834ff59e2...` | **SUCCESS** |
| **ACN** | 40,264 | 0 | 0 | `cabed9046c4d1a24...` | **SUCCESS** |
| **TMO** | 38,755 | 0 | 0 | `95d14cf356eff295...` | **SUCCESS** |
| **LIN** | 35,535 | 0 | 0 | `a7f3b0efedb8f2d6...` | **SUCCESS** |
| **NFLX** | 50,340 | 0 | 0 | `4a15fe69c6dd374d...` | **SUCCESS** |
| **AMD** | 48,197 | 0 | 0 | `c00ece54bb0c1fd3...` | **SUCCESS** |
| **DIS** | 46,621 | 0 | 0 | `bc38cf9f5249394a...` | **SUCCESS** |
| **ABT** | 46,499 | 0 | 0 | `1bbe2b89f6c2477e...` | **SUCCESS** |
| **ORCL** | 49,444 | 0 | 0 | `53592fce06823a3e...` | **SUCCESS** |
| **INTC** | 50,958 | 0 | 0 | `df7ce9ee7fb43294...` | **SUCCESS** |
| **CMCSA** | 48,459 | 0 | 0 | `997d89d0becdf4da...` | **SUCCESS** |
| **VZ** | 49,299 | 0 | 0 | `e4a21cedda458d3e...` | **SUCCESS** |
| **QCOM** | 45,490 | 0 | 0 | `56d423439155d16e...` | **SUCCESS** |
| **TXN** | 39,872 | 0 | 0 | `8063367089f888e3...` | **SUCCESS** |
| **DHR** | 37,314 | 0 | 0 | `46ecc5351e614ff5...` | **SUCCESS** |
| **PM** | 33,859 | 0 | 0 | `344ce5d1242cfdf3...` | **SUCCESS** |
| **CAT** | 38,394 | 0 | 0 | `1842c581fba73380...` | **SUCCESS** |
| **NKE** | 49,346 | 0 | 0 | `01d8c139e1f660a8...` | **SUCCESS** |
| **IBM** | 40,676 | 0 | 0 | `00283db35a191a99...` | **SUCCESS** |
| **UNP** | 27,353 | 0 | 0 | `0f0ce4770a41c62e...` | **SUCCESS** |
| **LOW** | 30,694 | 0 | 0 | `f271bf1bbe3845ff...` | **SUCCESS** |
| **SPY** | 51,456 | 0 | 0 | `8ccd6065c5eeaa07...` | **SUCCESS** |


---

## 3. Data Quality Findings
1. **Clock Monotonicity**: 100% of timestamps are strictly ascending in UTC and converted to US/Eastern.
2. **OHLC Consistency**: 0 invalid OHLC anomalies detected across all 2,227,357 bars.
3. **No Synthetic Gap Filling**: Zero synthetic bars generated; missing IEX ticks are maintained as true market gaps.
4. **Premarket Coverage**: Alpaca IEX supplies true premarket trades (08:30–09:30 ET) with average coverage rate of **78.4%** across liquid symbols.
