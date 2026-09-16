# Moneymaker Live Data Provenance & Evidence Classification Standard

## 1. Overview & Policy Statement
To prevent overfitting, backtest optimism, and data fabrication, Moneymaker enforces a strict **Data Provenance Architecture**. Every performance statistic, P&L metric, fill price, and trade displayed in the Workstation UI or analyzed by the AI Copilot must explicitly declare its evidence origin.

---

## 2. Six Authoritative Provenance Classifications

| Evidence Classification | Badge | Criteria & Verification Rules |
| :--- | :--- | :--- |
| **`BROKER_LIVE`** | `LIVE` | Backed by a live brokerage order ID (`broker_order_id`), real timestamps, verified cash deductions, and real market session execution. |
| **`BROKER_PAPER`** | `PAPER` | Executed against a live broker API paper/sandbox environment with real-time market data but simulated capital. |
| **`FORWARD_SHADOW`** | `SHADOW` | Generated in forward out-of-sample real-time conditions using strictly past-only data without sending broker orders. |
| **`HISTORICAL`** | `HISTORICAL` | Derived from historical walk-forward backtest data with strict embargo and purging rules. |
| **`SIMULATED`** | `SIMULATED` | Monte Carlo, synthetic stress shocks, or bootstrap permutations. |
| **`PROJECTED`** | `PROJECTED` | Parametric capacity model extrapolations (e.g. theoretical capacity above validated capital). |

---

## 3. Live Evidence Audit Engine (`audit_live_evidence`)
The `DataProvenanceEngine` (`src/workstation/provenance.py`) audits database rows:
1. **`VERIFIED_LIVE`**: Contains valid broker order identifier, valid execution timestamp, recognized strategy ID, and valid price/shares.
2. **`UNVERIFIED_LIVE`**: Claims `BROKER_LIVE` but lacks a valid broker order ID or timestamp.
3. **`INVALID_LIVE_LABEL`**: Contains synthetic tokens (e.g. `MOCK`, `SYNTHETIC`) while masquerading as `BROKER_LIVE`. Fails with audit alarm.

---

## 4. UI Display Guarantee
The Workstation UI visibly renders colored `EvidenceBadge` chips across all dashboards, position tables, trade journals, strategy cards, and AI chat bubbles. Evidence classification is never hidden from the user.
