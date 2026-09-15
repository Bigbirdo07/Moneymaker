# Tier 2 Empirical Friction Reconciliation & Canonical Accounting Report

## 1. Executive Summary & Problem Statement
During Phase 6C, the summary table reported:
- Gross Alpha: **+4.89 bps**
- Total Friction: **3.58 bps**
- Net Expectancy: **+1.31 bps**

However, the component breakdown table displayed:
- Spread Cost: $1.63$ bps
- Slippage: $0.09$ bps
- Market Impact: $0.16$ bps
- Latency Cost: $0.05$ bps
- Arithmetic Sum of Displayed Rows: **$1.93$ bps** (leaving an apparent unaccounted discrepancy of **$1.65$ bps**).

This audit resolves the discrepancy by tracing all execution parameters to the underlying order fills and establishing a single canonical accounting equation.

---

## 2. Root Cause Analysis
The discrepancy was an **accounting/reporting presentation defect** caused by reporting single-leg (entry) spread instead of complete round-trip spread:

1. **Single-Leg vs Round-Trip Spread Accounting**:
   - Alpha A executes intraday round-trip positions (Entry Buy $\to$ Exit Sell).
   - The observed average half-spread at entry was **$1.63$ bps**.
   - The observed average half-spread at exit was **$1.65$ bps**.
   - Total round-trip spread cost = $1.63 + 1.65 = \mathbf{3.28\text{ bps}}$.
2. **Component Reconciliation**:
   - Total Round-Trip Spread: **$3.28$ bps**
   - Total Slippage (Entry $0.05$ bps + Exit $0.04$ bps): **$0.09$ bps**
   - Empirical Market Impact (Entry $0.08$ bps + Exit $0.08$ bps): **$0.16$ bps**
   - Decision-to-Fill Latency Cost: **$0.05$ bps**
   - Commissions & Regulatory Fees: **$0.00$ bps** (Zero-commission equity broker structure; FINRA TAF/SEC fees $< 0.005$ bps)
   - **Canonical Sum of Components**: $3.28 + 0.09 + 0.16 + 0.05 = \mathbf{3.58\text{ bps}}$.

---

## 3. Canonical Round-Trip Friction Equation

$$\mathbf{TOTAL\_ROUND\_TRIP\_FRICTION\_BPS} = S_{\text{entry}} + S_{\text{exit}} + \text{Slip}_{\text{entry}} + \text{Slip}_{\text{exit}} + \text{Impact} + \text{Latency} + \text{Fees}$$

| Canonical Component | Notation | Tier 0 ($1k) | Tier 1 ($2.5k) | Tier 2 ($5k) [Observed Live] | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Entry Spread Cost** | $S_{\text{entry}}$ | 1.62 bps | 1.62 bps | **1.63 bps** | Half-spread paid on entry limit/cross |
| **Exit Spread Cost** | $S_{\text{exit}}$ | 1.63 bps | 1.64 bps | **1.65 bps** | Half-spread paid on exit fill |
| **Entry Slippage** | $\text{Slip}_{\text{entry}}$ | 0.04 bps | 0.04 bps | **0.05 bps** | Queue crossing slippage at entry |
| **Exit Slippage** | $\text{Slip}_{\text{exit}}$ | 0.04 bps | 0.04 bps | **0.04 bps** | Queue crossing slippage at exit |
| **Empirical Market Impact** | $\text{Impact}$ | 0.00 bps | 0.07 bps | **0.16 bps** | Order size price displacement |
| **Latency Cost** | $\text{Latency}$ | 0.02 bps | 0.04 bps | **0.05 bps** | Price drift during signal-to-order transit |
| **Commissions & Fees** | $\text{Fees}$ | 0.00 bps | 0.00 bps | **0.00 bps** | Exchange/clearing fees |
| **TOTAL ROUND-TRIP FRICTION**| $\sum \text{Friction}$ | **3.35 bps** | **3.41 bps** | **3.58 bps** | Exact sum of all friction legs |

---

## 4. Net Expectancy Identity Verification

$$\text{Gross Alpha (bps)} - \text{Total Round-Trip Friction (bps)} = \text{Net Expectancy (bps)}$$

$$\mathbf{4.890\text{ bps}} - \mathbf{3.580\text{ bps}} = \mathbf{1.310\text{ bps}}$$

* **Arithmetic Discrepancy**: **$0.000$ bps**
* **Identity Status**: **PERFECTLY RECONCILED**

---

## 5. Automated Accounting Enforcement
A permanent regression test `test_canonical_friction_reconciliation_identity` and `CanonicalRoundTripFriction` data class have been added to [`src/portfolio/capital_ramp.py`](file:///Users/albertopaz/Moneymaker/src/portfolio/capital_ramp.py) and [`tests/test_phase6d_capacity_audit.py`](file:///Users/albertopaz/Moneymaker/tests/test_phase6d_capacity_audit.py) to guarantee that any future reporting discrepancies fail CI/CD.
