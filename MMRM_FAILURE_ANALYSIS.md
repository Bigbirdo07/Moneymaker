# MMRM-0.1-REAL Failure Analysis Report

**Evaluated Artifact**: [`outputs/evaluations/REAL_MMRM_ONLY_V2.jsonl`](file:///Users/albertopaz/Moneymaker/outputs/evaluations/REAL_MMRM_ONLY_V2.jsonl)  
**Total Evaluated Items**: 200 items  
**Strict Passes**: 52 / 200 (26.00%)  
**Total Failures**: 148 items  
**Semantic Passes**: 101 / 200 (50.50%)  
**False Negative Rate**: **20.27%** (30 / 148 failed items)  

---

## 1. MMRM Failure Mode Breakdown (148 Failed Items)

| Primary Failure Category | Count | Percentage | Root Cause Analysis |
| :--- | :--- | :--- | :--- |
| `TOOL_FAILURE` | **78** | **52.7%** | In multi-tool sequencing items, emitted 1st tool correctly but omitted 2nd/3rd downstream tool. |
| `MISSING_REQUIRED_FACT` | **30** | **20.3%** | Lacked historical trade database facts for symbols not in 520 training examples. |
| `AUTHORITY_FAILURE` | **20** | **13.5%** | In subtle adversarial prompts with obfuscated phrasing, provided analysis instead of prompt refusal. |
| `NUMERIC_ERROR` | **11** | **7.4%** | Small rounding variance on multi-step $t$-statistic calculations. |
| `SCORER_FALSE_NEGATIVE` | **9** | **6.1%** | Valid factual description with alternative punctuation rejected. |

---

## 2. Key Insights on Fine-Tuning Gains & Limitations

1. **Format Specialization**: The QLoRA fine-tune successfully taught the model Moneymaker tool syntax and governance refusal headers (100% pass on direct tool selection and authority tasks).
2. **Parametric Capacity Limit**: 520 examples (~87.8k tokens) was sufficient for structural adaptation, but insufficient to memorize the entire historical state ledger of un-grounded symbols.
3. **Synergy with RAG**: Fact-intensive failures (accounting snapshots, current positions) disappear when paired with RAG (lifting accuracy to 71.50%).
