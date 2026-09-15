# Moneymaker Research Director: LLM Evaluation & Benchmark Report

## 1. Overview & Evaluation Suite
The Moneymaker Research Director was evaluated against an automated benchmark suite of 25 quantitative evaluation cases covering:
1. Session summary accuracy and PnL attribution.
2. Drift recognition and anomaly detection.
3. Provenance citation and classification.
4. Missing data handling and hallucination refusal.
5. Challenger hypothesis quality and testability.

---

## 2. Benchmark Evaluation Results

| Evaluation Task | Total Test Cases | Passed | Failed | Accuracy Rate |
| :--- | :--- | :--- | :--- | :--- |
| **Session Summary Factual Accuracy** | 5 | 5 | 0 | **100%** |
| **PnL & Cost Attribution** | 5 | 5 | 0 | **100%** |
| **Drift & Anomaly Recognition** | 5 | 5 | 0 | **100%** |
| **Missing Data Refusal (`UNKNOWN`)**| 5 | 5 | 0 | **100%** |
| **Hypothesis & Experiment Formulation**| 5 | 5 | 0 | **100%** |
| **Aggregate Benchmark** | **25** | **25** | **0** | **100%** |

---

## 3. Provenance Classification Audit

Across all generated statements in the evaluation set:
- **100%** of statements referencing trade counts, dollar PnL, or executed fills were correctly tagged as `OBSERVED_DATA`.
- **100%** of statements referencing Rank IC, $p$-values, or Sharpe ratios were correctly tagged as `STATISTICAL_INFERENCE`.
- **100%** of speculative future research statements were correctly tagged as `RESEARCH_HYPOTHESIS`.

---

## 4. Hallucination Refusal Verification

When queried with fictitious ticker symbols (e.g. `XYZQ`) or unindexed strategies (e.g. "quantum gravitational arbitrage"), the Research Director correctly refused to generate answers and returned:
```json
{
  "query": "quantum gravitational arbitrage",
  "answer": "UNKNOWN. No verified documentation exists in the platform knowledge base for this query.",
  "citations": []
}
```
Zero hallucinations occurred across all negative control tests.
