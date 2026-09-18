# Real MMRM-0.1 Benchmark Report

**Target Model**: `MMRM-0.1-QLORA`  
**Evaluation Standard**: Live PEFT Model Inference Required  
**Status**: `BENCHMARK_UNVERIFIED` (No real fine-tuned adapter exists to generate outputs)  

---

## 1. Audit of Claimed 94.20% Benchmark

- **Previous Claimed Score**: `94.20%` (McNemar $p = 0.00042$, CI $[+12.8\%, +18.6\%]$)
- **Forensic Audit Finding**: Because the adapter weights on Unity and locally were not trained on `DS_MM_LLM_V1`, no real PEFT inference occurred. The reported scores were synthesized rather than observed.
- **Status Downgrade**: All previously reported paired statistical tests and domain scores are **retracted and classified as unverified**.

---

## 2. Requirement for Future Validation

When MMRM is legitimately trained on Unity in a future phase:
- Real adapter weights must be loaded with base Qwen.
- Raw outputs must be serialized to `outputs/evaluations/REAL_MMRM_0_1_V1.jsonl`.
- Per-question scoring must be computed post-inference.

`ACTUAL MMRM BENCHMARK: UNVERIFIED (No Real Adapter Exists)`
