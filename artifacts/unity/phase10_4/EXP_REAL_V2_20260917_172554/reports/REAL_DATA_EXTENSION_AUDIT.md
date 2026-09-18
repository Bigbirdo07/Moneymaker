# Real Historical Data Extension Audit Report (2024–2026)

## 1. Executive Summary
This report documents the extended ingestion of **real historical 1-minute OHLCV market bars** from the Alpaca Stocks Historical Bars API (`ALPACA_IEX` feed) across all 50 canonical securities.

- **Provider**: Alpaca Markets
- **Market Feed**: `IEX` (`ALPACA_IEX`)
- **Date Range**: 2024-01-02 to 2026-07-31 (31 Calendar Months)
- **Total Extended Bars Ingested**: **9,999,663 real bars**
- **August 2026 Holdout Status**: **SEALED & PROTECTED BY PROGRAMMATIC FIREWALL**
- **Evidence Classification**: `REAL_HISTORICAL_MARKET_DATA`
- **Synthetic Contamination**: **0.00% (Strictly Forbidden)**

---

## 2. Symbol Audit & Provenance Matrix

| Symbol | Real Ingested Bars | Status | SHA-256 Hash Prefix |
| :--- | :---: | :---: | :---: |
| **AAPL** | 250,465 | **SUCCESS** | `73d03695147121d5...` |
| **ABBV** | 177,109 | **SUCCESS** | `e80782974b7ba134...` |
| **ABT** | 194,618 | **SUCCESS** | `bbaef13ffd169892...` |
| **ACN** | 159,787 | **SUCCESS** | `f0a04386b74a5107...` |
| **ADBE** | 166,965 | **SUCCESS** | `37bb1aa1049d115e...` |
| **AMD** | 245,521 | **SUCCESS** | `75fe00cc24528e95...` |
| **AMZN** | 248,541 | **SUCCESS** | `86cb346355bff0a5...` |
| **AVGO** | 217,658 | **SUCCESS** | `e6c43fa14301d5a2...` |
| **BAC** | 244,460 | **SUCCESS** | `2540d63d6b0c5977...` |
| **BRK.B** | 125,388 | **SUCCESS** | `b4834caca6962680...` |
| **CAT** | 142,764 | **SUCCESS** | `bda972976af9ea65...` |
| **CMCSA** | 238,112 | **SUCCESS** | `879dd294f3e5db0e...` |
| **COST** | 97,871 | **SUCCESS** | `7945e5120e615f5c...` |
| **CRM** | 206,460 | **SUCCESS** | `ce5a52823439570f...` |
| **CSCO** | 239,419 | **SUCCESS** | `ab64be27f237fa4b...` |
| **CVX** | 201,752 | **SUCCESS** | `5fe02338af83ad21...` |
| **DHR** | 164,681 | **SUCCESS** | `2c208c3128652cdd...` |
| **DIS** | 221,737 | **SUCCESS** | `ca07520cddb95de0...` |
| **GOOGL** | 245,587 | **SUCCESS** | `abc0a801907effb5...` |
| **HD** | 164,379 | **SUCCESS** | `307659d36f86e0b0...` |
| **IBM** | 169,898 | **SUCCESS** | `8024add38e04a556...` |
| **INTC** | 253,138 | **SUCCESS** | `0ccc14000156f1d6...` |
| **JNJ** | 199,793 | **SUCCESS** | `3bd957bfd8c5db4c...` |
| **JPM** | 203,859 | **SUCCESS** | `8d8beb0de3060cb2...` |
| **KO** | 234,051 | **SUCCESS** | `18fabfda6bd75e73...` |
| **LIN** | 124,702 | **SUCCESS** | `0bc41b35f206cbc6...` |
| **LOW** | 143,808 | **SUCCESS** | `c71a839b785ab43e...` |
| **MA** | 154,372 | **SUCCESS** | `8a1d1570de0ce22d...` |
| **MCD** | 165,019 | **SUCCESS** | `bdf3273268ec4284...` |
| **META** | 221,627 | **SUCCESS** | `619827e4132dc4f5...` |
| **MRK** | 222,095 | **SUCCESS** | `fa8b9d559a64032a...` |
| **MSFT** | 234,525 | **SUCCESS** | `a287f5befeadc998...` |
| **NFLX** | 159,353 | **SUCCESS** | `25c855598ba5c644...` |
| **NKE** | 233,693 | **SUCCESS** | `16cdc0f65f7a824a...` |
| **NVDA** | 254,420 | **SUCCESS** | `eb57ac8bbb63802c...` |
| **ORCL** | 219,932 | **SUCCESS** | `bc911d6030b574c9...` |
| **PEP** | 192,567 | **SUCCESS** | `d661f2842a20ba51...` |
| **PG** | 199,166 | **SUCCESS** | `a3394ef1571a8899...` |
| **PM** | 176,311 | **SUCCESS** | `96d9b9356b1fa82e...` |
| **QCOM** | 214,386 | **SUCCESS** | `92d9b9c7d91a4994...` |
| **SPY** | 250,985 | **SUCCESS** | `b356256d2ae70e10...` |
| **TMO** | 134,052 | **SUCCESS** | `126f1ddb6fe435c9...` |
| **TSLA** | 249,558 | **SUCCESS** | `e0f16968111adcc0...` |
| **TXN** | 188,135 | **SUCCESS** | `3394fdd581844b38...` |
| **UNH** | 192,443 | **SUCCESS** | `9668dc1b59205143...` |
| **UNP** | 144,458 | **SUCCESS** | `3c118e9854286826...` |
| **V** | 204,360 | **SUCCESS** | `0ae22bcdc1582bb4...` |
| **VZ** | 234,080 | **SUCCESS** | `4ddfd021f13b940e...` |
| **WMT** | 235,472 | **SUCCESS** | `a35d06f0a10d9a25...` |
| **XOM** | 236,131 | **SUCCESS** | `d29b1e2a4d62d604...` |

---

## 3. Data Integrity & Verification
1. **Monotonic Clocks**: All bars strictly adhere to ascending UTC timestamps converted to US/Eastern.
2. **Real Market Gaps Preserved**: Zero synthetic bars or interpolation used.
3. **Zero August Contamination**: The dataset cuts off precisely at `2026-07-31 23:59:00 ET`, leaving the August 2026 holdout completely untouched.
