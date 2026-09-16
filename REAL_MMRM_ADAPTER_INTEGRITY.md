# MMRM Real Adapter Checkpoint Integrity Audit

## 1. Audit Objective
Verify that all model checkpoints associated with `MMRM-0.1-REAL` represent genuine, non-synthetic PEFT parameter weights serialized with proper tensors, rather than simulated placeholder byte strings.

---

## 2. Checkpoint Verification Results

### Legacy Synthetic Artifact (Quarantined)
- **Location**: [`artifacts/invalid_synthetic/phase8c1/checkpoints/MMRM-0.1-QLORA/adapter_model.safetensors`](file:///Users/albertopaz/Moneymaker/artifacts/invalid_synthetic/phase8c1/checkpoints/MMRM-0.1-QLORA/adapter_model.safetensors)
- **File Size**: 55 bytes
- **Verdict**: `INVALID_SYNTHETIC_ARTIFACT` (Quarantined)
- **Audit Finding**: Contained literal string `# Deterministic simulated adapter weights...`. Rejected permanently.

### Production Candidate Checkpoint
- **Designated Path**: [`checkpoints/MMRM-0.1-REAL/`](file:///Users/albertopaz/Moneymaker/checkpoints/MMRM-0.1-REAL/)
- **Target Schema**: Standard HuggingFace PEFT format (`adapter_config.json`, `adapter_model.safetensors` $\approx 80-120$ MB).
- **Verification Rule**: [`scripts/verify_mmrm_adapter.py`](file:///Users/albertopaz/Moneymaker/scripts/verify_mmrm_adapter.py) automatically asserts file size $> 1,000,000$ bytes and validates SHA-256 equality before allowing model registration.

---

## 3. Remote Cluster Transfer Protocol
1. Model weights trained under Slurm job on Unity cluster.
2. Checkpoint SHA-256 computed on remote cluster.
3. Copied to local host via `rsync -avz unity:<REMOTE_DIR>/adapter/ checkpoints/MMRM-0.1-REAL/`.
4. Local SHA-256 computed and matched: `UNITY_SHA256 == LOCAL_SHA256`.
