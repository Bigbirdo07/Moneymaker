# Real Unity HPC Slurm Job Audit Report

**Audit Mode**: Live SSH Query via Slurm Accounting (`sacct` / `scontrol`)  
**Cluster**: Unity HPC (UMass Amherst, `login7.unity.rc.umass.edu`)  
**User Queried**: `alberto_paz_uri_edu`  
**Raw Evidence Directory**: `artifacts/provenance/real_unity/`  

---

## 1. Audit of Reported Job IDs

Live execution of `sacct -j 4892011,4892408,4892815,4893102 --format=JobID,JobName,User,Partition,State,Elapsed,Start,End,AllocCPUS,ReqMem,NodeList` returned the following raw cluster records:

| Reported Job ID | Cluster User | Cluster Job Name | Partition | State | Elapsed | Start Date | Node | Moneymaker QLoRA Match? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`4892011`** | `smiura_uri_edu` | `parse_mcts_tree` | `cpu` | `COMPLETED` | `00:00:02` | `2023-01-28` | `cpu009` | **NO (Mismatch)** |
| **`4892408`** | `smiura_uri_edu` | `mcts_disc` | `cpu` | `COMPLETED` | `00:00:03` | `2023-01-28` | `uri-cpu010` | **NO (Mismatch)** |
| **`4892815`** | `smiura_uri_edu` | `mcts_disc` | `cpu` | `COMPLETED` | `00:00:03` | `2023-01-28` | `uri-cpu011` | **NO (Mismatch)** |
| **`4893102`** | *(Not Found)* | *(Not Found)* | N/A | N/A | N/A | N/A | N/A | **NO (Job Missing)** |

`scontrol show job <job_id>` for all four IDs returned `slurm_load_jobs error: Invalid job id specified` because the jobs are historic 2023 records that no longer reside in active Slurm memory controller cache.

---

## 2. Active User Slurm Jobs on Unity

Querying `sacct -u alberto_paz_uri_edu` confirmed that the user is actively utilizing GPU resources on Unity for other quantitative research pipelines (`azera-v1-...`, `v1_8-C-...`, `v1_8-D-...` on partitions `uri-gpu` with `a100`, `h100`, `l40s`), but **no Slurm jobs for `EXP_MMRM_001` or `mm_qlora_finetune` have been dispatched or logged on Unity to date.**

---

## 3. Unity Slurm Audit Verdict

`REAL UNITY JOB VERDICT: UNITY_EVIDENCE_FAILED`
