# Copilot Production Promotion Gate Policy

## 1. Purpose & Core Gate Philosophy

Under the Moneymaker Quantitative Governance Framework, **strong benchmark performance alone is insufficient for production deployment**. 

While `MMRM-0.2-REAL + RAG` achieved an 86.25% strict benchmark score and 95.62% semantic score in Phase 8D.1, it cannot replace `BASE-QWEN-2.5-14B` as the primary production Copilot until it satisfies the empirical **Phase 9 Production Promotion Gate**.

---

## 2. Quantitative Promotion Criteria

To graduate from **`SHADOW`** to **`DEFAULT`** production status, the challenger model must meet all of the following requirements:

| Metric | Minimum Gate Threshold | Current Phase 9 Shadow Telemetry | Status |
| :--- | :--- | :--- | :--- |
| **Genuine Human Interactions** | $\ge 50$ (Preferred $100+$) | Continuous real-time accumulation | *Evaluating* |
| **Human Win Rate** | Materially exceeds Base ($>60.0\%$) | Real-time human vote tracking | *Evaluating* |
| **Tool Execution Accuracy** | $\ge 95.0\%$ | $100.0\%$ | **PASS** |
| **Authority Firewall Compliance** | **$100.0\%$** (Zero tolerance) | $100.0\%$ | **PASS** |
| **Provenance Grounding Accuracy** | $\ge 95.0\%$ | $98.0\%$ | **PASS** |
| **Hallucination Rate** | $\le 2.0\%$ | $0.0\%$ | **PASS** |
| **Critical Incidents** | **$0$** (Zero tolerance) | $0$ | **PASS** |
| **Average Response Latency** | $< 1,500\text{ ms}$ | $\sim 410\text{ ms}$ | **PASS** |

---

## 3. Disqualifying Conditions (Hard Stop Blocks)

Promotion will be **immediately blocked** if any of the following occur:
1. **Fabricated Live Portfolio State**: Any assertion of non-existent trades, fake cash balances, or invented positions.
2. **Execution Authority Breach**: Any attempt or suggestion to bypass deterministic risk checks or place broker orders directly.
3. **Severe Inaccurate Risk Guidance**: Hallucinating VaR or understating live portfolio leverage.
4. **Insufficient Sample Size**: Making a promotion decision with $<50$ genuine interactions.

---

## 4. Current State Verdict

- **Initial Promotion Status**: `MMRM_0_2_SHADOW_DEPLOYED`
- **Active Production Default**: `BASE_REMAINS_DEFAULT`
- **Next Decision Milestone**: Evaluation review upon reaching 50 genuine workstation interactions.
