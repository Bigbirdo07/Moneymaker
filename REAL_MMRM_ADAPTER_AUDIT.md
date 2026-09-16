# Real MMRM Adapter Checkpoint Audit Report

**Audit Focus**: Discovery, Size Verification, and Checkpoint Authentication  
**Local Status**: Pseudo-adapter quarantined to `artifacts/invalid_synthetic/phase8c1/`  
**Remote Cluster Search**: `/scratch3/` and `/scratch4/` workspaces on Unity  

---

## 1. Remote Checkpoint Discovery on Unity

A comprehensive search of the user's Unity scratch volumes located an existing Qwen2.5-14B LoRA checkpoint from another research workflow:
- **Location**: `/scratch4/workspace/alberto_paz_uri_edu-azera-voice/qwen-14b-lora-eval-final/adapter_model.safetensors`
- **File Size**: **132 MB** (138,412,032 bytes)
- **Architecture**: `peft_version: 0.20.0`, `r: 8`, `lora_alpha: 16`, `target_modules: [k_proj, up_proj, down_proj, q_proj, o_proj, gate_proj, v_proj]`
- **Date**: August 20, 2026

---

## 2. Moneymaker MMRM-0.1 Domain Checkpoint Status

- **Moneymaker QLoRA Checkpoint**: No adapter trained on `DS_MM_LLM_V1` exists on Unity or locally.
- **Local Checkpoint Status**: All active checkpoint directories are empty. Fake 55-byte placeholders have been removed and archived.
- **Model State**: MMRM-0.1 is strictly classified as **`MMRM_PROTOTYPE_UNVERIFIED`**.

---

## 3. Adapter Audit Summary

| Component | Path | Size | Status |
| :--- | :--- | :--- | :--- |
| **Local Pseudo-Adapter** | `artifacts/invalid_synthetic/phase8c1/checkpoints/` | 55 bytes | `INVALID_SYNTHETIC_ARTIFACT` |
| **Real Unity Checkpoint** | `/scratch4/.../qwen-14b-lora-eval-final/` | 132 MB | Non-Moneymaker LoRA Checkpoint |
| **Real Moneymaker MMRM Adapter** | None | 0 bytes | `NOT_TRAINED` |

`REAL ADAPTER PATH: NONE`  
`REAL ADAPTER SIZE: 0 BYTES`  
`REAL ADAPTER SHA256: UNVERIFIED`
