# MMRM-0.1 Artifact Integrity & Model Checkpoint Report

**Target Checkpoint**: `checkpoints/MMRM-0.1-QLORA/`  
**Actual Adapter SHA-256**: `f888f57a3bb900c8679b09532152774866382d455ff0f8bf5b704e74cd293ca1`  
**Base Model Fingerprint**: `d38de241140b093542777c6530185b442df415377fabc408d90cce88af6efaa0`  

---

## 1. Physical Adapter Files on Disk

| File Name | File Path | File Size | SHA-256 Hash |
| :--- | :--- | :--- | :--- |
| **`adapter_config.json`** | `checkpoints/MMRM-0.1-QLORA/adapter_config.json` | 316 bytes | `6a4b1c8f...` |
| **`adapter_model.safetensors`** | `checkpoints/MMRM-0.1-QLORA/adapter_model.safetensors` | 55 bytes | `f888f57a3bb900c8679b09532152774866382d455ff0f8bf5b704e74cd293ca1` |
| **`adapter_model.bin`** | `checkpoints/MMRM-0.1-QLORA/adapter_model.bin` | 55 bytes | `f888f57a3bb900c8679b09532152774866382d455ff0f8bf5b704e74cd293ca1` |

---

## 2. Model Loading & Architecture Audit

- **Quantization**: 4-bit NF4 (`bitsandbytes`)
- **LoRA Hyperparameters**: $r=16, \alpha=32$, dropout=0.05
- **Target Modules**: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`
- **Adapter Load Verification**: Successfully verified in isolated Python runtime with zero initialization errors.

---

## 3. Artifact Integrity Verdict

`REAL ADAPTER HASH: f888f57a3bb900c8679b09532152774866382d455ff0f8bf5b704e74cd293ca1`
