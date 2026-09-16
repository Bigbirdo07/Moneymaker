# Moneymaker Experiment Registry Architecture

## 1. Purpose & Core Governance

The **Moneymaker Experiment Registry** (`src/research/experiment_registry.py`) provides a cryptographically verifiable ledger for all quantitative research runs executed locally or on the Unity HPC cluster.

Every quantitative hypothesis must be recorded as an immutable experiment before results are analyzed.

---

## 2. Experiment Schema & Lifecycle States

### Experiment Record Fields
- `experiment_id`: Unique identifier (e.g. `EXP_ALPHA_B_HOLDING_SWEEP_001`).
- `created_at`: UTC ISO timestamp.
- `strategy_id`: Target strategy (`ALPHA_A`, `ALPHA_B`, `PORTFOLIO_ALLOCATOR`).
- `git_commit`: Exact Git commit SHA of the codebase executing the job.
- `dataset_hash`: SHA-256 hash of the immutable dataset manifest.
- `config_hash`: SHA-256 hash of the experiment parameter JSON.
- `code_hash`: SHA-256 hash of the core mathematical runner code.
- `random_seed`: Seed used for deterministic reproducibility.
- `compute_target`: Target compute (`LOCAL_CPU`, `LOCAL_GPU`, `UNITY_CPU`, `UNITY_GPU`, `UNITY_HIGHMEM`).
- `status`: Lifecycle state (see below).
- `slurm_job_id`: Slurm job identifier assigned by cluster scheduler.
- `runtime_seconds`: Wall-clock execution duration.
- `hardware_info`: Hardware metrics (GPU model, VRAM, RAM, CPU threads).
- `metrics`: Quantitative performance dictionary (Sharpe, Net Expectancy, Max Drawdown).
- `artifact_paths`: Paths to generated model checkpoints, prediction ledgers, and equity curves.

### Lifecycle State Machine
```
[CREATED] ──> [QUEUED] ──> [RUNNING] ──┬─> [FAILED] ──> [REJECTED]
                                       │
                                       └─> [COMPLETED] ──> [VALIDATION_FAILED]
                                                  │
                                                  └──> [CANDIDATE] ──> [APPROVED]
```

1. `CREATED`: Initial parameter manifest recorded locally.
2. `QUEUED`: Submitted to cluster scheduler.
3. `RUNNING`: Executing on compute node.
4. `FAILED`: Job crashed or encountered runtime error.
5. `COMPLETED`: Run finished successfully and produced artifacts.
6. `VALIDATION_FAILED`: Failed out-of-sample, embargo, or leakage verification.
7. `CANDIDATE`: Passed statistical significance checks, pending human review.
8. `APPROVED`: Manually promoted for forward-shadow evaluation.
9. `REJECTED`: Rejected due to insufficient edge, friction sensitivity, or data snooping.

---

## 3. Cryptographic Verification & Ingestion

When artifacts return from Unity HPC:
1. `dataset_hash` is matched against the local dataset manifest.
2. `config_hash` is recomputed against parameter inputs.
3. `code_hash` is verified against current repository state.
4. **Any mismatch immediately triggers `VALIDATION_FAILED` / `REJECTED`**, preventing contaminated or unverified research from entering the evaluation pipeline.
