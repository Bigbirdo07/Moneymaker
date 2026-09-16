# Real Base Model Benchmark Report: Qwen2.5-14B-Instruct

**Target Model**: `Qwen2.5-14B-Instruct`  
**Evaluation Standard**: Live Autoregressive Token Generation Required  
**Status**: Pre-Inference Baseline Reference  

---

## 1. Audit of Baseline Claims

- **Previous Claimed Score**: `78.50%`
- **Audit Finding**: The previous evaluation outputs in Phase 8C/8C.1 were generated from hardcoded template strings rather than live forward passes through a loaded `Qwen2.5-14B-Instruct` model instance on an A100/H100 node.
- **Status Downgrade**: The score of 78.5% is marked **`UNVERIFIED_PRETRAINED_BASELINE`**.

---

## 2. Benchmark Protocol for Real Evaluation

To establish a verified baseline:
1. Load `Qwen2.5-14B-Instruct` in an isolated PyTorch environment on an active GPU node.
2. Execute greedy generation ($\text{temperature}=0.0, \text{max\_new\_tokens}=512$) on all 10 frozen benchmark prompts (`BM-001` to `BM-010`).
3. Store complete raw generated text in `outputs/evaluations/REAL_BASE_QWEN_V1.jsonl`.
4. Score outputs using deterministic keyword, tool-schema, and refusal matchers.

`ACTUAL BASE BENCHMARK: UNVERIFIED (Awaiting GPU Forward Pass)`
