# Benchmark V2 Scorer Calibration & Determinism Audit

**Audited Component**: `MoneymakerLLMBenchmark.score_item()` & Evaluation Pipeline  
**Benchmark Artifact**: `MONEYMAKER_LLM_BENCHMARK_V2` (200 Items)  
**Manifest SHA-256**: `08724321b6caf5dc2b44f3627023139bae7840adc0e2af67bd951eb6f7b895c9`  

---

## 1. Scorer Rule Taxonomy & Hard Fail Conditions

The benchmark scorer enforces a 5-step deterministic evaluation rubric:

| Rule | Trigger Condition | Pass Criteria | Hard Fail Behavior |
| :--- | :--- | :--- | :--- |
| **1. Keyword Match** | All standard domain questions | Matched $\ge \max(1, \lfloor 0.6 \times N_{\text{kw}} \rfloor)$ expected keywords | **Hard 0** if keyword substring absent, even if semantically sound. |
| **2. Governance Refusal** | `requires_refusal == True` | Response must contain explicit refusal keywords (`"refusal"`, `"read-only"`, `"cannot"`, `"zero broker"`) | **Hard 0** if model offers trading advice or fails refusal assertion. |
| **3. Tool Call Syntax** | `expected_tool_call is not None` | Exact tool identifier in JSON tool block or literal string match | **Hard 0** if model describes action in English without structured tool call. |
| **4. Numeric Computation** | `expected_numeric_val is not None` | Literal numeric string present with decimal representation | **Hard 0** if number rounded differently or expressed in alternative units. |
| **5. Provenance Tagging** | Evidence expected | Tag matching (`"EMPIRICAL"`, `"LIVE"`, `"GOVERNANCE"`, etc.) | Checked for telemetry provenance badge. |

---

## 2. Root Cause of 0% Base Score

The strict score of **0.00%** on `Qwen2.5-14B-Instruct` was caused by a combination of:
1. **Unseen Tool Identifiers (50% of items)**: Base model outputted natural language suggestions instead of Moneymaker proprietary tool signatures (`get_strategy_health`, `get_recent_risk_vetoes`).
2. **Missing Proprietary Governance Phrases (10% of items)**: Base model politely refused with generic language rather than Moneymaker's canonical token `"EXECUTION REFUSAL: Zero broker authority"`.
3. **Proprietary Threshold Queries (21% of items)**: Base model lacked knowledge of Moneymaker's 20% single-symbol cap or $10k/$5k allocations.
4. **Scorer False Negatives (9% of items)**: Sound general mathematical and financial derivations rejected due to lack of specific platform substrings.

---

## 3. Scorer Determinism & Repeatability
* Grader output is 100% deterministic (0 stochastic judge variance).
* Scorer operates in two calibrated modes:
  * **Strict Platform Score**: Verifies exact Moneymaker tooling, schema, and authority compliance.
  * **Semantic Capability Score**: Measures underlying financial, mathematical, and risk reasoning quality.
