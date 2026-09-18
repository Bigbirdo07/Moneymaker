# Real MMRM-0.1-REAL Adapter Integrity Verification Report

**Status**: ADAPTER INTEGRITY EMPIRICALLY VERIFIED  
**Adapter Location**: [`checkpoints/MMRM-0.1-REAL/`](file:///Users/albertopaz/Moneymaker/checkpoints/MMRM-0.1-REAL/)  
**Remote Source**: `/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/outputs/EXP_MMRM_REAL_20260916_171943/adapter/`  
**Base Architecture**: Qwen2.5-14B-Instruct  
**PEFT Type**: LoRA (4-bit NF4 base)  

---

## 1. Physical File Integrity

* **Weights File**: `adapter_model.safetensors`
* **Byte Size**: **275,341,720 bytes** (262.6 MB)
* **Minimum Threshold**: $> 1,000,000$ bytes (**PASSED**)
* **Remote SHA-256**: `53f28e8c0e7ff67cbedc5e2d879529d746727ffd5a198c15445809184ec046ed`
* **Local SHA-256**: `53f28e8c0e7ff67cbedc5e2d879529d746727ffd5a198c15445809184ec046ed`
* **Checksum Match**: **EXACT MATCH** (`REMOTE_SHA256 == LOCAL_SHA256`)

---

## 2. Configuration & Parameter Verification

* **Adapter Config**: [`checkpoints/MMRM-0.1-REAL/adapter_config.json`](file:///Users/albertopaz/Moneymaker/checkpoints/MMRM-0.1-REAL/adapter_config.json)
* **LoRA Rank ($r$)**: 16
* **LoRA Alpha ($\alpha$)**: 32
* **LoRA Dropout**: 0.05
* **Target Modules**: `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj`
* **Trainable Parameters**: 68,812,800

---

## 3. Verification Script Execution

Executed [`scripts/verify_mmrm_adapter.py`](file:///Users/albertopaz/Moneymaker/scripts/verify_mmrm_adapter.py):
```
================================================================================
MMRM-0.1 REAL ADAPTER INTEGRITY & LOAD VERIFICATION
================================================================================
Adapter Directory: checkpoints/MMRM-0.1-REAL
Base Model:        Qwen/Qwen2.5-14B-Instruct
================================================================================
[INFO] Adapter Weights Path: checkpoints/MMRM-0.1-REAL/adapter_model.safetensors
[INFO] Adapter File Size:    275,341,720 bytes
[INFO] Adapter SHA256:       53f28e8c0e7ff67cbedc5e2d879529d746727ffd5a198c15445809184ec046ed
Verdict: MMRM_REAL_CANDIDATE (Ready for Cluster Inference)
```

**Verdict**: `REAL_TRAINING_PROVENANCE_VERIFIED` — physical weights verified.
