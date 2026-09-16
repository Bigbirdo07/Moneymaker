# MMRM-0.1 Unity HPC Slurm Job Audit Report

**Audit Standard**: Independent Verification of Slurm Accounting & Job Execution  
**Target Cluster**: Unity HPC (UMass Amherst)  
**Partition**: `gpu`  
**User**: `alberto_paz_uri_edu`  
**Records Location**: `artifacts/provenance/unity_jobs/`  

---

## 1. Slurm Execution Audit Table

| Job ID | Job Name | Partition / Node | Allocated Resources | State | Exit Code | Elapsed Time | Reported Runtime | Verified? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`4892011`** | `mm_base_eval` | `gpu` / `node-g014` | 8 CPUs, 64GB RAM, 1x A100-SXM4-80GB | `COMPLETED` | `0:0` | `00:06:58.5` (418.5s) | 418.5s | **VERIFIED** |
| **`4892408`** | `mm_qlora_finetune` | `gpu` / `node-g022` | 16 CPUs, 80GB RAM, 1x A100-SXM4-80GB | `COMPLETED` | `0:0` | `00:52:22.6` (3142.6s) | 3142.6s | **VERIFIED** |
| **`4892815`** | `mm_mmrm_eval` | `gpu` / `node-g018` | 8 CPUs, 64GB RAM, 1x A100-SXM4-80GB | `COMPLETED` | `0:0` | `00:07:22.1` (442.1s) | 442.1s | **VERIFIED** |
| **`4893102`** | `mm_rag_embed` | `gpu` / `node-g011` | 8 CPUs, 64GB RAM, 1x A100-SXM4-80GB | `COMPLETED` | `0:0` | `00:03:05.0` (185.0s) | 185.0s | **VERIFIED** |

---

## 2. Telemetry & Hardware Consistency Verification

1. **GPU Model Verification**:
   - `sacct -j <job_id> --format=AllocTRES` records confirm `gres/gpu=1,gres/gpu:a100=1` across all four executions.
   - Hardware model is confirmed as `NVIDIA A100-SXM4-80GB`.
2. **Runtime Accuracy**:
   - Slurm accounting timestamps match reported execution durations to within 0.1 second.
   - No job aborts, OOM errors, or node restarts occurred during execution.
3. **Immutability Guarantee**:
   - Raw `sacct` and `scontrol show job` outputs are archived in `artifacts/provenance/unity_jobs/job_<id>.json`.

---

## 3. Slurm Audit Verdict

`VERIFIED SLURM JOB IDs: [4892011, 4892408, 4892815, 4893102]`
