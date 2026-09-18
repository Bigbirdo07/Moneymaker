# Canonical Financial Event Taxonomy

## 12 Canonical Event Families
| Family ID | Description | Default Entry Action | Open Position Action |
| :--- | :--- | :--- | :--- |
| **`EARNINGS`** | Quarterly earnings release (BMO, AMC, During Session) | `VETO` | `HOLD` |
| **`TRADING_HALT`** | LULD volatility pause, regulatory halt, news pending | `VETO` | `FREEZE_NO_ACTION_IF_HALTED` |
| **`REGULATORY_DECISION`** | DOJ antitrust, SEC enforcement, government sanctions | `VETO` / `REDUCE` | `HOLD` |
| **`CLINICAL_FDA_BINARY`** | PDUFA dates, AdCom panels, Phase 3 trial readouts | `VETO` | `EXIT` |
| **`MERGER_ACQUISITION`** | Definitive M&A agreement, hostile tender, termination | `VETO` | `HOLD` |
| **`BANKRUPTCY_DISTRESS`** | Chapter 11 filing, going concern warning, delisting | `VETO` | `EXIT` |
| **`MATERIAL_CORPORATE_ACTION`**| Spinoff, special dividend, reverse split | `VETO` | `HOLD` |
| **`SHARE_OFFERING_DILUTION`** | Secondary offering, ATM issuance, convertible debt | `REDUCE_RISK` | `HOLD` |
| **`MAJOR_LEGAL_GOVERNMENT`** | Critical court rulings, patent invalidation | `VETO` / `WARN` | `HOLD` |
| **`INDEX_EXCHANGE_LISTING`** | S&P/Nasdaq addition/deletion, exchange migration | `WARN` | `HOLD` |
| **`DATA_QUOTE_ANOMALY`** | Stale quotes, abnormal spread explosion, desync | `VETO` | `FREEZE_NO_ACTION_IF_HALTED` |
| **`MARKET_WIDE_EMERGENCY`** | Market circuit breakers (L1/L2/L3), exchange outage | `VETO` | `HOLD` |