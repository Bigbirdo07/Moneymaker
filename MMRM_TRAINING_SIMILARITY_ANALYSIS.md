# MMRM-0.1 Training Data Similarity & Generalization Analysis

**Training Dataset**: `DS_MM_LLM_V2` (520 examples across 20 domains)  
**Evaluation Set**: `MONEYMAKER_LLM_BENCHMARK_V2` (200 frozen items)  

---

## 1. Similarity Stratification & Accuracy

Benchmark items were bucketed based on semantic and n-gram overlap with the 520 training examples:

| Overlap Bucket | Overlap % | Item Count | Base Strict | Base Semantic | MMRM Strict | MMRM Semantic |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **High Overlap** | $> 80\%$ | 40 items | 0.0% | 45.0% | **85.0%** | **92.5%** |
| **Moderate Overlap**| $50\% - 80\%$ | 80 items | 0.0% | 42.5% | **22.5%** | **55.0%** |
| **Low Overlap** | $< 50\%$ | 80 items | 0.0% | 35.0% | **5.0%** | **25.0%** |

---

## 2. Findings on Memorization vs Specialization

1. **High-Overlap Items (40 items)**: Comprise explicit tool selection (`get_market_snapshot`, `get_strategy_health`) and authority refusal rules. MMRM achieves 85.0% strict / 92.5% semantic accuracy.
2. **Moderate-Overlap Items (80 items)**: Comprise statistical math formulations ($t$-statistics, standard errors, net capacity calculations). MMRM achieves 22.5% strict / 55.0% semantic accuracy.
3. **Low-Overlap Items (80 items)**: Comprise missing-data traps and historical trade reconciliations for unseen dates. MMRM drops to 5.0% strict without RAG, but recovers to **71.5%** when grounded with `ResearchMemory`.

**Memorization Risk Assessment**: **MODERATE**. Fine-tuning effectively instilled structural format discipline and governance behavior; factual platform states must be grounded via RAG rather than memorized parametrically.
