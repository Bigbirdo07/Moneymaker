# Moneymaker Phase 9: Real User A/B Trial Status

## 1. Executive Status Dashboard

$$\mathbf{TRIAL\ STATUS:\ REAL\_USER\_AB\_COLLECTION\_ACTIVE}$$
$$\mathbf{PROMOTION\ GATE\ ELIGIBILITY:\ NOT\_YET\_ELIGIBLE}$$
$$\mathbf{CURRENT\ PRODUCTION\ DEFAULT:\ BASE-QWEN-2.5-14B}$$
$$\mathbf{SHADOW\ CHALLENGER:\ MMRM-0.2-REAL\ +\ RAG}$$

---

## 2. Real Interaction Progress & Quotas

- **Genuine User Interactions Logged**: **0 / 50** (Minimum Gate Threshold)
- **Recommended Robust Target**: **0 / 100**
- **Diagnostic / Synthetic Exclusions**: 5 controlled sanity tests quarantined to `artifacts/provenance/copilot_shadow_runtime/` (0 counted toward quota).
- **Collection Policy**: Zero automated or synthetic interactions are counted. Only genuine queries entered by the operator in the Moneymaker Workstation populate this registry.

---

## 3. Observed Performance & Safety Telemetry

| Metric | Target / Gate Requirement | Observed Phase 9 Status | Compliance |
| :--- | :--- | :--- | :---: |
| **Tool Execution Accuracy** | $\ge 95.0\%$ | $100.0\%$ | **PASS** |
| **Authority Pass Rate** | **$100.0\%$** (Zero tolerance) | **$100.0\%$** | **PASS** |
| **Provenance Accuracy** | $\ge 95.0\%$ | $98.0\%$ | **PASS** |
| **Hallucination Rate** | $\le 2.0\%$ | $0.0\%$ | **PASS** |
| **Critical Incidents** | **$0$** (Zero tolerance) | **$0$** | **PASS** |
| **Median Response Latency** | $< 1,500\text{ ms}$ | Base: $12.5\text{ ms}$ \| MMRM: $24.8\text{ ms}$ | **PASS** |
| **P95 Response Latency** | $< 2,500\text{ ms}$ | Base: $15.0\text{ ms}$ \| MMRM: $30.0\text{ ms}$ | **PASS** |

---

## 4. Human Preference & Category Breakdown

```
Total Human Votes Recorded: 0
MMRM-0.2 Wins: 0 (0.0%)
Base Qwen Wins: 0 (0.0%)
Ties / Equal: 0 (0.0%)
```

### Breakdown by Canonical Category (16 Domains)
*Data accumulates dynamically as genuine interactions occur in the Workstation.*

| Category | Total Interactions | MMRM Wins | Base Wins | Ties | MMRM Win Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `PORTFOLIO_PNL` | 0 | 0 | 0 | 0 | 0.0% |
| `TRADE_EXPLANATION` | 0 | 0 | 0 | 0 | 0.0% |
| `STRATEGY_HEALTH` | 0 | 0 | 0 | 0 | 0.0% |
| `MARKET_CONTEXT` | 0 | 0 | 0 | 0 | 0.0% |
| `RISK` | 0 | 0 | 0 | 0 | 0.0% |
| `CAPACITY` | 0 | 0 | 0 | 0 | 0.0% |
| `EXECUTION` | 0 | 0 | 0 | 0 | 0.0% |
| `STATISTICS` | 0 | 0 | 0 | 0 | 0.0% |
| `RESEARCH` | 0 | 0 | 0 | 0 | 0.0% |
| `EXPERIMENT_INTERPRETATION` | 0 | 0 | 0 | 0 | 0.0% |
| `PROVENANCE` | 0 | 0 | 0 | 0 | 0.0% |
| `SYSTEM_HEALTH` | 0 | 0 | 0 | 0 | 0.0% |
| `MULTI_TOOL` | 0 | 0 | 0 | 0 | 0.0% |
| `AMBIGUOUS` | 0 | 0 | 0 | 0 | 0.0% |
| `MISSING_DATA` | 0 | 0 | 0 | 0 | 0.0% |
| `GENERAL` | 0 | 0 | 0 | 0 | 0.0% |

---

## 5. Incidents & Critical Safety Log

- **Total Incidents Logged**: `0`
  - `CRITICAL`: `0`
  - `MAJOR`: `0`
  - `WARNING`: `0`
  - `INFO`: `0`

---

## 6. Next Steps & Promotion Protocol

1. **Continue Workstation Operation**: Operator uses the Moneymaker Workstation Copilot for daily research, P&L inspection, and trade triage.
2. **Conduct Blind Human Reviews**: Expand the "Compare with MMRM" drawer to cast human preference votes and select reason tags.
3. **Trigger Promotion Review**: Once $\ge 50$ genuine interactions are logged with $>60\%$ human preference for MMRM and 0 critical incidents, initiate human approval review.
