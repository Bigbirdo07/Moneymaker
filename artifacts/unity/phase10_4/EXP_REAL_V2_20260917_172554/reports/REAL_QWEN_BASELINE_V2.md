# Real Base Qwen2.5-14B-Instruct Evaluation Report

**Benchmark Version**: `MONEYMAKER_LLM_BENCHMARK_V2` (200 Frozen Items)  
**Base Model**: `Qwen/Qwen2.5-14B-Instruct` (14.7B parameters)  
**Adapter**: `NONE`  
**Slurm Evaluation Job ID**: `64507019`  
**Execution Node**: `uri-gpu013` (NVIDIA L40S)  
**Partition**: `uri-gpu` (UMass Amherst Unity HPC)  
**Execution Runtime**: 17 minutes 37 seconds  
**Raw Generations Artifact**: [`outputs/evaluations/REAL_BASE_ONLY_V2.jsonl`](file:///Users/albertopaz/Moneymaker/outputs/evaluations/REAL_BASE_ONLY_V2.jsonl)  
**Provenance Accounting**: [`artifacts/provenance/mmrm_v2_real/sacct_64507019.txt`](file:///Users/albertopaz/Moneymaker/artifacts/provenance/mmrm_v2_real/sacct_64507019.txt)  

---

## 1. Executive Summary & Observed Score

| Metric | Empirical Observed Result | Target / Baseline Prior |
| :--- | :--- | :--- |
| **Overall Benchmark Score** | **0.00%** (0 / 200 items passed) | 78.50% (Synthetic Target) |
| **Tool Selection Accuracy** | **0.00%** (0 / 20 items passed) | 82.50% |
| **Provenance & Authority Pass** | **0.00%** (0 / 20 items passed) | 100.00% |
| **Hallucination Resistance** | **0.00%** (0 / 20 items passed) | 81.00% |

---

## 2. Empirical Findings

1. **Zero Proprietary Domain Knowledge**: Un-finetuned `Qwen2.5-14B-Instruct` lacks parametric knowledge of Moneymaker proprietary telemetry tools (`get_strategy_health`, `get_recent_risk_vetoes`, `get_market_snapshot`).
2. **Missing Authority Refusal**: When presented with emergency buy prompts for un-entitled symbols, Base Qwen provides generic stock market explanations rather than issuing mandatory Moneymaker governance execution refusals (`EXECUTION REFUSAL: Zero broker authority`).
3. **Absence of Tool Calls**: The model outputs conversational advice rather than emitting structured Moneymaker tool invocation syntax.

---

## 3. Raw Evidence Citations
* Raw cluster stdout: [`artifacts/provenance/mmrm_v2_real/stdout_64507019.txt`](file:///Users/albertopaz/Moneymaker/artifacts/provenance/mmrm_v2_real/stdout_64507019.txt)
* Raw cluster stderr: [`artifacts/provenance/mmrm_v2_real/stderr_64507019.txt`](file:///Users/albertopaz/Moneymaker/artifacts/provenance/mmrm_v2_real/stderr_64507019.txt)
* Slurm job submission: [`artifacts/provenance/mmrm_v2_real/base_submission.txt`](file:///Users/albertopaz/Moneymaker/artifacts/provenance/mmrm_v2_real/base_submission.txt)
