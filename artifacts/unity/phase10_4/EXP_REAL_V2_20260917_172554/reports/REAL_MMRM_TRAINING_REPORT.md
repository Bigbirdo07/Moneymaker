# Real MMRM-0.1 QLoRA Training Experiment Report

# Real MMRM-0.1-REAL QLoRA Training Report

**Status**: REAL TRAINING COMPLETED & PROVENANCE VERIFIED  
**Experiment ID**: `EXP_MMRM_REAL_20260916_171943`  
**Slurm Job ID**: `64516939`  
**Partition**: `uri-gpu`  
**Execution Node**: `uri-gpu004`  
**GPU Hardware**: NVIDIA A100-SXM4-80GB (1 GPU allocated, 8 CPUs, 64 GB RAM)  
**Cluster Host**: `login7.unity.rc.umass.edu` (UMass Amherst Unity HPC)  
**Execution Timestamp**: `2026-09-16T17:19:43+00:00`  
**Total Training Runtime**: 438.5 seconds (7 min 18 sec)  
**Exit State**: `COMPLETED` (Exit Code `0:0`)

---

## 1. Provenance & Training Parameters

* **Base Model**: `Qwen/Qwen2.5-14B-Instruct`
* **Base Model Path**: `/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`
* **Quantization**: 4-bit NF4 (`load_in_4bit=True`, `bnb_4bit_quant_type="nf4"`, `bnb_4bit_use_double_quant=True`, `torch_dtype=bfloat16`)
* **PEFT / LoRA Hyperparameters**:
  * $r = 16$
  * $\alpha = 32$
  * Dropout $= 0.05$
  * Target Modules: `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]`
  * Trainable Parameters: **68,812,800** (0.4637% of 14,838,846,464 total parameters)
* **Optimizer**: `paged_adamw_8bit`
* **Learning Rate**: $2 \times 10^{-4}$ (with linear decay)
* **Epochs**: 3 (75 total optimization steps)
* **Batch Size**: 2 per device (gradient accumulation: 8, effective batch size: 16)
* **Training Dataset**: `data/moneymaker_llm/v2/train.jsonl` (400 examples, 29,730 tokens, SHA-256: `7b48d5de4303a5085fa40feca6c3ab7c18f170623b2eb06ab1f15a402150a433`)

---

## 2. Training Loss Progression (Empirical Telemetry)

| Step | Epoch | Training Loss | Gradient Norm | Learning Rate |
| :--- | :--- | :--- | :--- | :--- |
| **10** | 0.40 | 2.6690 | 0.5880 | $1.760 \times 10^{-4}$ |
| **20** | 0.80 | 0.8839 | 0.9232 | $1.493 \times 10^{-4}$ |
| **30** | 1.20 | 0.2305 | 0.5722 | $1.227 \times 10^{-4}$ |
| **40** | 1.60 | 0.1183 | 0.3819 | $9.600 \times 10^{-5}$ |
| **50** | 2.00 | 0.1081 | 0.3014 | $6.933 \times 10^{-5}$ |
| **60** | 2.40 | 0.0914 | 0.2635 | $4.267 \times 10^{-5}$ |
| **70** | 2.80 | 0.0857 | 0.2401 | $1.600 \times 10^{-5}$ |
| **75 (Final)** | 3.00 | **0.5639 (Cumulative)** | — | $0.000 \times 10^{-4}$ |

* **Throughput**: 2.736 samples/sec, 0.171 steps/sec
* **VRAM Usage**: ~14.8 GB allocated under NF4 4-bit quantization on 80GB A100-SXM4

---

## 3. Generated Physical Artifacts

| File | Size | SHA-256 Checksum |
| :--- | :--- | :--- |
| `adapter_model.safetensors` | **275,341,720 bytes** (262.6 MB) | `53f28e8c0e7ff67cbedc5e2d879529d746727ffd5a198c15445809184ec046ed` |
| `adapter_config.json` | 1,293 bytes | `6043c8fe14498a34e0bd15ca62f970ac4efb5b52250d3cc7eed6b3032cc65c20` |
| `tokenizer.json` | 11,421,991 bytes | `2f55e63353d3d978b390d346bae531be8b83bc9532c0be500d62b7253aa4c595` |
| `tokenizer_config.json` | 693 bytes | `2e3bd3cb5055f7a903a54e7062b2fd14d21b70f4174c3ffcd9fc81ec50a25631` |
| `README.md` | 5,474 bytes | `f059cf61afef4a75b7df826aa1922425a87f90290bb471ebd9b56544f2ea85cf` |

* **Local Verification**: Copied via `rsync` to [`checkpoints/MMRM-0.1-REAL/`](file:///Users/albertopaz/Moneymaker/checkpoints/MMRM-0.1-REAL/). Local SHA-256 matches remote SHA-256 exactly. Checked via [`scripts/verify_mmrm_adapter.py`](file:///Users/albertopaz/Moneymaker/scripts/verify_mmrm_adapter.py).
