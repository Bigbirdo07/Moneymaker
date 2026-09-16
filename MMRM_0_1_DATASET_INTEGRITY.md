# MMRM-0.1 Dataset Integrity & Leakage Verification Report

**Dataset ID**: `DS_MM_LLM_V1`  
**Data Directory**: `data/moneymaker_llm/`  
**Actual Dataset SHA-256**: `06cbc1cde936ff7e05e77f4bd7f7d04809a9ff906e12945654cc55aec469e53d`  

---

## 1. Physical Dataset File Inventory

| Split | File Path | Total Records | File Size | SHA-256 Fingerprint |
| :--- | :--- | :--- | :--- | :--- |
| **Train** | `data/moneymaker_llm/train.jsonl` | 11 records | 11,036 bytes | `07ac9072413982701e6a147424b9a304e0e5671ef3bdfaa73c52e6d634288bcf` |
| **Validation** | `data/moneymaker_llm/val.jsonl` | 2 records | 1,868 bytes | `71a066be242d66f8e709a34da413919e8b7d903e659b8eb6a978f84447385da4` |
| **Internal Test** | `data/moneymaker_llm/test.jsonl` | 4 records | 3,310 bytes | `a0b6a2726afd106fe1d1dc4eaec2b55f11075fc88b7764f69ad99ad55c46e27b` |
| **TOTAL** | **All 3 Splits** | **17 records** | **16,214 bytes** | **`06cbc1cde936ff7e05e77f4bd7f7d04809a9ff906e12945654cc55aec469e53d`** |

---

## 2. Benchmark Leakage Audit

- **Audit Methodology**: Cross-comparison of all prompt text in `data/moneymaker_llm/*.jsonl` against the 10 frozen evaluation items in `MONEYMAKER_LLM_BENCHMARK_V1` (`BM-001` through `BM-010`).
- **Exact Overlap**: **0 / 17 examples (0.0%)**.
- **Near-Duplicate Overlap**: **0 / 17 examples (0.0%)**.
- **Contamination Verdict**: **CLEAN (Zero Benchmark Leakage)**.

---

## 3. Dataset Integrity Verdict

`REAL DATASET HASH: 06cbc1cde936ff7e05e77f4bd7f7d04809a9ff906e12945654cc55aec469e53d`
