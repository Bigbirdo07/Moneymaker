# Real Training Dataset Audit & Scale Assessment: `DS_MM_LLM_V1`

**Dataset Identifier**: `DS_MM_LLM_V1`  
**Physical Storage**: `data/moneymaker_llm/` (`train.jsonl`, `val.jsonl`, `test.jsonl`)  
**Actual Dataset SHA-256**: `06cbc1cde936ff7e05e77f4bd7f7d04809a9ff906e12945654cc55aec469e53d`  

---

## 1. Actual Dataset Inventory & Scale Review

The serialized dataset `DS_MM_LLM_V1` contains exactly **17 examples**:

| Split | Records | Total Bytes | Average Length | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`train.jsonl`** | 11 | 11,036 bytes | ~1,003 bytes / record | Proof-of-concept instructional examples |
| **`val.jsonl`** | 2 | 1,868 bytes | ~934 bytes / record | Validation loss sanity |
| **`test.jsonl`** | 4 | 3,310 bytes | ~827 bytes / record | Internal generalization test |
| **TOTAL** | **17** | **16,214 bytes** | **~953 bytes / record** | **Proof-of-Concept Prototype** |

---

## 2. Scientific Scale Classification

- **Prototype Status**: 17 examples is a proof-of-concept dataset schema, not a full-scale domain adaptation corpus (which typically requires 1,000–5,000+ diverse examples).
- **Domain Coverage**: The 17 examples span all 10 core quantitative domains (A through J), including 9 tool-use examples and 3 negative/refusal authority examples.
- **Leakage Status**: 0.00% benchmark contamination against `MONEYMAKER_LLM_BENCHMARK_V1`.

---

## 3. Dataset Scale Recommendation

Future MMRM development (Phase 8D) should expand `DS_MM_LLM_V1` to $\ge 1,500$ authentic multi-turn trading traces and market regime scenarios before submitting full production training runs on Unity.

`ACTUAL TRAINING EXAMPLE COUNT: 17 PROTOTYPE EXAMPLES`
