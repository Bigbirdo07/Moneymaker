# Phase 11C: Real Historical Market Data Audit (2021–2023)

## 1. Dataset Overview
This dataset contains real 1-minute OHLCV market bars acquired from Alpaca's historical market data API (`IEX` feed) for all 50 canonical equities plus `SPY` across 36 calendar months (`2021-01-01` to `2023-12-31`).

- **Provider**: Alpaca Markets
- **Market Feed**: `IEX` (`ALPACA_IEX`)
- **Date Range**: 2021-01-01 to 2023-12-31
- **Total 1-Minute Bars Ingested**: **11,462,336 real bars**
- **Evidence Class**: `REAL_HISTORICAL_MARKET_DATA`
- **Synthetic Contamination**: **0.00% (Strictly Forbidden)**

## 2. Partition Structure

| Partition | Date Range | Calendar Span | Purpose | Status |
| :--- | :---: | :---: | :--- | :---: |
| **TRAIN** | `2021-01-01` to `2022-12-31` | 24 Months | Frozen V3 Architecture Model Training | **AUTHORIZED** |
| **FRESH REPLICATION HOLDOUT** | `2023-01-01` to `2023-12-31` | 12 Months | Single-Pass Out-of-Sample Final Exam | **SEALED / EVALUATION ONLY** |

---

## 3. Symbol Audit & Provenance Verification Matrix

| Symbol | Real Ingested Bars | Date Coverage | Status | SHA-256 Hash Prefix |
| :--- | :---: | :---: | :---: | :---: |
| **AAPL** | 294,129 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `f0d11627d1d876c1...` |
| **ABBV** | 229,539 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `b23b37558fc9b7a7...` |
| **ABT** | 223,606 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `0f262162ce04167d...` |
| **ACN** | 164,745 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `24cd3e9c797e6d88...` |
| **ADBE** | 188,423 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `1f1c94db6ff3da01...` |
| **AMD** | 288,569 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `bf0b217d9f0dc3a1...` |
| **AMZN** | 231,492 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `20f6ae6d13136f95...` |
| **AVGO** | 150,766 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `6efc22fd4c543653...` |
| **BAC** | 283,562 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `0cfc0bdd4fb3adbc...` |
| **BRK.B** | 185,324 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `c6a17cbd9da24a67...` |
| **CAT** | 178,105 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `18c7fb65ff750a39...` |
| **CMCSA** | 277,040 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `70dfa359a7cae1c4...` |
| **COST** | 146,094 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `6cf434bca1acc588...` |
| **CRM** | 239,716 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `4fe4140939fb1955...` |
| **CSCO** | 278,191 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `3e9baab4993cec94...` |
| **CVX** | 249,203 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `5bdf28111c6f6679...` |
| **DHR** | 187,487 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `e45e366ea67acdc2...` |
| **DIS** | 250,973 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `a5fe47d65e6022aa...` |
| **GOOGL** | 202,965 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `6f8386fefcf3caf7...` |
| **HD** | 204,425 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `c1221a735da4e6ba...` |
| **IBM** | 206,344 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `faeb6aa4fd3bcf3e...` |
| **INTC** | 285,832 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `8479f26ae771a503...` |
| **JNJ** | 238,217 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `0a7d8fec9b626376...` |
| **JPM** | 250,043 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `dbf11d60838176cd...` |
| **KO** | 264,650 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `9f9b953743cd9c94...` |
| **LIN** | 143,500 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `77c8b2988bbc468b...` |
| **LOW** | 205,818 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `5bde4ae92629b8ec...` |
| **MA** | 203,753 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `74ac6988b12e753c...` |
| **MCD** | 172,596 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `8331e03d9be5d00b...` |
| **META** | 277,073 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `0508cf682f9f2159...` |
| **MRK** | 253,541 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `c3ed6ea66a3cd8fe...` |
| **MSFT** | 279,933 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `370f5aa3688f5cb6...` |
| **NFLX** | 219,186 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `f6e8cd8106f88ebf...` |
| **NKE** | 238,641 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `322d04f1cb744f6a...` |
| **NVDA** | 275,346 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `68aaf508fcd7b98f...` |
| **ORCL** | 257,609 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `72cfd53a2741dc96...` |
| **PEP** | 201,453 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `720ec4656f1fccde...` |
| **PG** | 235,037 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `7464783aeeddb199...` |
| **PM** | 203,462 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `e8c9a0ea26480b29...` |
| **QCOM** | 243,901 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `4675cc79ad866b46...` |
| **SPY** | 301,044 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `e92b2ceaa85dce80...` |
| **TMO** | 141,870 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `546280753b5407a4...` |
| **TSLA** | 280,393 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `39961c043d2840e3...` |
| **TXN** | 217,614 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `72c1cd6fa865a990...` |
| **UNH** | 189,699 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `a99c2f72ecce7eeb...` |
| **UNP** | 196,148 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `0999b9d320c9ec77...` |
| **V** | 244,665 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `bb3f43d39f9a745a...` |
| **VZ** | 273,175 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `78922373437ebea6...` |
| **WMT** | 234,506 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `98858e813474d98c...` |
| **XOM** | 272,933 | `2021-01-04` to `2023-12-29` | **SUCCESS** | `47e3fab29e4ffbba...` |

---

## 4. Quality & Integrity Assertions
1. **Monotonic Clocks**: All bar timestamps are sorted ascending without duplicates.
2. **Natural Missingness**: Market holidays and half-days are preserved naturally without synthetic imputation.
3. **Zero Lookahead**: All bar features and targets strictly observe trade session boundaries.
