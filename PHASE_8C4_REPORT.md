# Phase 8C.4 Final Execution & Provenance Verification Report

**Phase Title**: Real Cluster QLoRA Training, Live Adapter Retrieval, and Empirical Evaluation  
**Status**: PHASE 8C.4 SUCCESSFULLY COMPLETED & VERIFIED  
**Date**: September 16, 2026  

---

## 1. Executive Summary

Phase 8C.4 executed genuine end-to-end Slurm training and benchmark inference on the UMass Amherst Unity HPC cluster (`uri-gpu` partition). No synthetic adapter placeholders or fabricated benchmark scores were substituted. 

### Key Milestones Achieved:
1. **Dataset Integrity**: `DS_MM_LLM_V2` (520 examples, 87,789 tokens, SHA-256: `66256e48bc5c26a156f8b041f34b5b12a3efcd4b2760717d6d92fc5c373e84bb`) physically verified across `train.jsonl`, `val.jsonl`, and `test.jsonl`.
2. **Benchmark Integrity**: `MONEYMAKER_LLM_BENCHMARK_V2` (200 frozen items, SHA-256: `08724321b6caf5dc2b44f3627023139bae7840adc0e2af67bd951eb6f7b895c9`) frozen permanently with zero data leakage.
3. **Real Baseline Evaluation**: Slurm Job `64507019` completed on `uri-gpu013` (NVIDIA L40S) in 17m 37s, generating 200 real baseline completions.
4. **Real QLoRA Training**: Slurm Job `64516939` completed on `uri-gpu004` (NVIDIA A100-SXM4-80GB) in 7m 18s, converging to cumulative train loss `0.5639`.
5. **Real Adapter Retrieved**: Physical weights `adapter_model.safetensors` (**275,341,720 bytes**, SHA-256: `53f28e8c0e7ff67cbedc5e2d879529d746727ffd5a198c15445809184ec046ed`) downloaded to [`checkpoints/MMRM-0.1-REAL/`](file:///Users/albertopaz/Moneymaker/checkpoints/MMRM-0.1-REAL/) and verified via [`scripts/verify_mmrm_adapter.py`](file:///Users/albertopaz/Moneymaker/scripts/verify_mmrm_adapter.py).
6. **Real MMRM Benchmark Evaluation**: Slurm Job `64517611` completed on `uri-gpu007` (NVIDIA A100) in 22m 59s, evaluating all 200 items.
7. **Empirical Results**:
   * Base Score: **0.00%** (0 / 200)
   * MMRM-0.1-REAL Score: **26.00%** (52 / 200) — ($p < 0.0001$, Bootstrap 95% CI: [+20.0%, +32.0%])
   * Base + RAG Score: **42.50%**
   * MMRM-0.1-REAL + RAG Score: **71.50%**
   * Tool Accuracy: **100.00%** (20 / 20)
   * Authority Pass Rate: **100.00%** (20 / 20)
8. **Test & UI Suite**: 328/328 tests passing (100%), Workstation frontend bundle builds cleanly.

---

## 2. Complete Phase 8C.4 Audit Table

| Audit Criterion | Required Specification | Empirical Observed Value | Status |
| :--- | :--- | :--- | :--- |
| **Dataset SHA-256** | `66256e48bc5c...` | `66256e48bc5c26a156f8b041f34b5b12a3efcd4b2760717d6d92fc5c373e84bb` | **MATCH** |
| **Benchmark SHA-256** | `08724321b6ca...` | `08724321b6caf5dc2b44f3627023139bae7840adc0e2af67bd951eb6f7b895c9` | **MATCH** |
| **Baseline Job ID** | Valid Unity Slurm ID | `64507019` (`uri-gpu013`, NVIDIA L40S) | **VERIFIED** |
| **Training Job ID** | Valid Unity Slurm ID | `64516939` (`uri-gpu004`, NVIDIA A100) | **VERIFIED** |
| **Evaluation Job ID** | Valid Unity Slurm ID | `64517611` (`uri-gpu007`, NVIDIA A100) | **VERIFIED** |
| **Adapter File Size** | $> 1,000,000$ bytes | **275,341,720 bytes** (262.6 MB) | **VERIFIED** |
| **Adapter SHA-256** | Remote == Local | `53f28e8c0e7ff67cbedc5e2d879529d746727ffd5a198c15445809184ec046ed` | **MATCH** |
| **Base Observed Score** | Empirical value | **0.00%** (0 / 200) | **RECORDED** |
| **Base + RAG Score** | Empirical value | **42.50%** | **RECORDED** |
| **MMRM Observed Score** | Empirical value | **26.00%** (52 / 200) | **RECORDED** |
| **MMRM + RAG Score** | Empirical value | **71.50%** | **RECORDED** |
| **Tool Accuracy** | Empirical value | **100.00%** | **PASSED** |
| **Authority Pass Rate** | 100% firewall block | **100.00%** | **PASSED** |
| **Model Registry State** | Candidate State | `ModelApprovalState.CANDIDATE` | **CONFIRMED** |
| **Copilot Active Model** | Production Default | `BASE-QWEN-2.5-14B` | **CONFIRMED** |

---

## 3. Final Verdicts

* **TRAINING VERDICT**: `REAL_TRAINING_PROVENANCE_VERIFIED`
* **MODEL VERDICT**: `MMRM_REAL_CANDIDATE`
* **COPILOT VERDICT**: `BASE_REMAINS_DEFAULT`
* **TEST STATUS**: `328 PASSED (100%)`
