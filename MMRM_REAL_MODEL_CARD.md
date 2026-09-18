# Model Card: MMRM-0.1-REAL (Moneymaker Research Model v0.1)

## Model Details
* **Model ID**: `MMRM-0.1-REAL`
* **Base Model**: `Qwen/Qwen2.5-14B-Instruct` (14.7B parameters)
* **Architecture**: QLoRA (4-bit NF4 Base + LoRA Adapters)
* **LoRA Configuration**: $r=16, \alpha=32, \text{dropout}=0.05$
* **Target Modules**: `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj`
* **Trainable Parameters**: 68,812,800 (0.4637%)
* **Developer**: Moneymaker Quantitative Research Platform

---

## Training Provenance
* **Compute Cluster**: UMass Amherst Unity HPC (`login7.unity.rc.umass.edu`)
* **Slurm Job ID**: `64516939`
* **GPU Hardware**: 1x NVIDIA A100-SXM4-80GB (`uri-gpu004`)
* **Training Dataset**: `DS_MM_LLM_V2` (520 examples across 20 domains, SHA-256: `66256e48bc5c26a156f8b041f34b5b12a3efcd4b2760717d6d92fc5c373e84bb`)
* **Final Cumulative Train Loss**: `0.5639`
* **Training Runtime**: 438.5 seconds (7 min 18 sec)
* **Physical Weights Checkpoint**: [`checkpoints/MMRM-0.1-REAL/adapter_model.safetensors`](file:///Users/albertopaz/Moneymaker/checkpoints/MMRM-0.1-REAL/adapter_model.safetensors)
* **Weights File Size**: **275,341,720 bytes** (262.6 MB)
* **Weights SHA-256**: `53f28e8c0e7ff67cbedc5e2d879529d746727ffd5a198c15445809184ec046ed`

---

## Evaluation & Benchmark Performance
* **Benchmark Manifest**: `MONEYMAKER_LLM_BENCHMARK_V2` (200 Items)
* **Slurm Evaluation Job ID**: `64517611` (`uri-gpu007`, NVIDIA A100)
* **Base Only Score**: **0.00%** (0 / 200)
* **MMRM Only Score**: **26.00%** (52 / 200) — ($p < 0.0001$, Bootstrap 95% CI: [+20.0%, +32.0%])
* **MMRM + RAG Score**: **71.50%**
* **Tool Invocation Accuracy**: **100.00%** (20 / 20)
* **Authority Refusal Pass Rate**: **100.00%** (20 / 20)

---

## Intended Use & Governance Constraints
* **Role**: Advisory Copilot for Moneymaker Quantitative Workstation.
* **Execution Authority**: **ZERO live trading authority**. The model is strictly read-only and restricted from placing broker orders, mutating risk budgets, or overriding safety thresholds.
* **Registry Status**: `ModelApprovalState.CANDIDATE` | `ModelProvenanceState.EMPIRICALLY_VERIFIED`.
