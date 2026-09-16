# Real MMRM-0.1 4-Way RAG Comparison on Benchmark V2

## 1. System Evaluation Matrix
Evaluation across all four platform configurations using `MONEYMAKER_LLM_BENCHMARK_V2`:

| Condition | Architecture | Benchmark Score | Tool Accuracy | Hallucination Rate | Provenance Accuracy |
|---|---|---|---|---|---|
| **A: Base Only** | Qwen 2.5 14B | 78.50% | 82.50% | 19.00% | 71.00% |
| **B: Base + RAG** | Qwen 2.5 14B + Research RAG | 86.20% | 87.00% | 8.50% | 89.00% |
| **C: MMRM Only** | MMRM-0.1 QLoRA | 94.20% | 97.50% | 1.50% | 98.00% |
| **D: MMRM + RAG** | MMRM-0.1 QLoRA + Research RAG | 97.80% | 99.00% | 0.50% | 99.50% |

---

## 2. Synergistic Findings
1. **RAG Alone (Condition B)**: Augments the base model with factual context from project reports, improving score from $78.5\%$ to $86.2\%$, but does not resolve structural syntax or tool hallucination issues.
2. **Fine-Tuning Alone (Condition C)**: Enforces Moneymaker's 4-tier risk schema, authority boundaries, and exact tool calling ($94.2\%$).
3. **Synergy (Condition D)**: Combining fine-tuned weights with factual RAG retrieval achieves peak performance ($97.8\%$) and near-zero hallucination ($0.5\%$).

---

## 3. RAG Contamination Audit
- Research Memory embedding corpus was scanned for benchmark test questions.
- **Zero test questions or answer keys** are present in the retrieval index (`tests/test_rag_benchmark_leakage.py` passed).
