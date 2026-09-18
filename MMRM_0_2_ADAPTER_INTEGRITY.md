# MMRM-0.2 Adapter Checkpoint Integrity Specification

**Target Model**: `MMRM-0.2-REAL`  
**Checkpoint Path**: `checkpoints/MMRM-0.2-REAL/`  
**Remote Target**: `/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/outputs/EXP_MMRM_0_2_REAL_*/adapter/`  
**Base Model**: `Qwen2.5-14B-Instruct`  
**Slurm Training Job**: `64519876`  

---

## 1. Physical Verification Criteria
1. `adapter_model.safetensors` file size must exceed $1,000,000$ bytes (expected $\approx 275$ MB).
2. Remote and local SHA-256 checksums must match exactly (`REMOTE_SHA256 == LOCAL_SHA256`).
3. Automated verification script [`scripts/verify_mmrm_adapter.py`](file:///Users/albertopaz/Moneymaker/scripts/verify_mmrm_adapter.py) must pass with `MMRM_REAL_CANDIDATE`.

---

## 2. Checkpoint Version Ledger

| Model ID | Status | File Size | Weights SHA-256 | Provenance State |
| :--- | :--- | :--- | :--- | :--- |
| `BASE-QWEN-2.5-14B` | Pretrained Base | 28.5 GB | Official HuggingFace Hub | `EMPIRICALLY_VERIFIED` |
| `MMRM-0.1-REAL` | V2 Empirical Checkpoint | **275,341,720 bytes** | `53f28e8c0e7ff67cbedc5e2d879529d746727ffd5a198c15445809184ec046ed` | `EMPIRICALLY_VERIFIED` |
| `MMRM-0.2-REAL` | V3 Training Scheduled | Target: ~275 MB | Pending Cluster Execution (Job `64519876`) | `UNVERIFIED` |
