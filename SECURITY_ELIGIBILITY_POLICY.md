# Security Eligibility Policy Specification (Phase B)

## 1. Objective & Scope
The **Security Eligibility Policy** establishes deterministic point-in-time criteria to reduce all ~33,000+ U.S. listed symbols down to liquid, standardized equity vehicles suitable for quantitative intraday momentum research.

---

## 2. Invariant Inclusion & Exclusion Rules

### A. Allowed Exchanges (Strict Primary Listing)
Only assets primarily listed on major regulated U.S. exchanges with consolidated tape feeds are permitted:
1. **NASDAQ** (National Association of Securities Dealers Automated Quotations)
2. **NYSE** (New York Stock Exchange)
3. **ARCA** (NYSE Arca)
4. **AMEX** (NYSE American)
5. **BATS** (Cboe BZX Exchange)

> [!CAUTION]
> **Strict OTC Exclusion**: All Over-The-Counter (OTC), Pink Sheet, Grey Market, and foreign unlisted shares are strictly disqualified under reason code `UNSUPPORTED_EXCHANGE`.

---

### B. Allowed Security Types
1. **Common Stock (`cs`)**: Primary operating company equity shares.
2. **Exchange-Traded Funds (`etf`)**: Standard unleveraged index and sector tracking vehicles (e.g. `SPY`, `QQQ`, `XLK`).
3. **American Depositary Receipts (`adr`)**: High-liquidity sponsored ADRs representing major foreign corporations.

---

### C. Prohibited Vehicle Structures
1. **Leveraged & Inverse Products**: All $2\times$, $3\times$, ultra, and inverse products are disqualified (`LEVERAGED_INVERSE_PRODUCT`) due to volatility drag and non-linear path dependency.
2. **Warrants, Rights, Preferreds**: Excluded under `UNSUPPORTED_SECURITY_TYPE`.
3. **Special Purpose Acquisition Companies (SPACs)**: Excluded under `SPECIAL_PURPOSE_ACQUISITION` due to arbitrary NAV arbitrage floors.
4. **Closed-End Funds & Mutual Funds**: Excluded under `UNSUPPORTED_SECURITY_TYPE`.

---

## 3. Machine-Readable Decision Code Schema

| Reason Code | Classification | Action Taken |
| :--- | :--- | :--- |
| `ELIGIBLE` | Passed all structural and exchange criteria | Forward to Market Data Quality Policy |
| `UNSUPPORTED_EXCHANGE` | OTC, Pink Sheets, foreign exchange | Excluded from daily universe manifest |
| `UNSUPPORTED_SECURITY_TYPE` | Warrant, Right, Preferred, CEF | Excluded from daily universe manifest |
| `LEVERAGED_INVERSE_PRODUCT` | 2x/3x/Inverse ETF | Excluded from daily universe manifest |
| `SPECIAL_PURPOSE_ACQUISITION` | SPAC vehicle | Excluded from daily universe manifest |
| `NOT_ACTIVE_STATUS` | Inactive, pending delisting | Excluded from daily universe manifest |
| `NOT_TRADABLE` | Broker untradable flag | Excluded from daily universe manifest |
