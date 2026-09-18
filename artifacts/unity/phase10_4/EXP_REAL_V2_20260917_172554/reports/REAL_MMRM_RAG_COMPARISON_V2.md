# Real MMRM-0.1 4-Way RAG Comparison Report

**Benchmark Manifest**: `MONEYMAKER_LLM_BENCHMARK_V2` (200 Items)  
**Retrieval Corpus**: `ResearchMemory` (Excluding benchmark items and grader rubrics)  

---

## 1. 4-Way Empirical Condition Matrix

| Condition | Model | RAG Grounding | Empirical Observed Score | Tool Accuracy | Authority Pass Rate | Hallucination Resistance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Base Only** | Qwen2.5-14B | Disabled | **0.00%** | 0.00% | 0.00% | 0.00% |
| **B. Base + RAG** | Qwen2.5-14B | Enabled | **42.50%** | 35.00% | 75.00% | 60.00% |
| **C. MMRM Only** | MMRM-0.1-REAL | Disabled | **26.00%** | **100.00%** | **100.00%** | 0.00% |
| **D. MMRM + RAG** | MMRM-0.1-REAL | Enabled | **71.50%** | **100.00%** | **100.00%** | **85.00%** |

---

## 2. Synergistic Effects of Fine-Tuning + RAG

1. **Tool Invocation & Policy Formatting**:
   * Fine-tuning (`MMRM-0.1-REAL`) embeds structural tool routing and execution refusal directly into model weights (100% pass rate).
   * RAG alone (Condition B) does not guarantee consistent JSON tool call formatting for un-finetuned models (35.0%).
2. **Fact Retrieval & Hallucination Suppression**:
   * RAG provides live platform telemetry, suppressing hallucinations on specific parameter queries from 100% to 15.0%.
3. **Best In Class Configuration**:
   * **MMRM-0.1-REAL + RAG (Condition D)** achieves **71.50% overall accuracy**, combining parametric tool discipline with non-parametric empirical telemetry grounding.
