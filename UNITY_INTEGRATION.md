# UMass Amherst Unity HPC Cluster Integration

## 1. Executive Summary & Architectural Principle

The Moneymaker Quantitative Research Platform integrates the **UMass Amherst Unity HPC cluster** as its asynchronous, heavy research-compute layer.

### Primary Architectural Principle: Asymmetric Decoupling
```
+------------------------------------+          +------------------------------------+
|       LIVE TRADING SYSTEM          |          |          UNITY HPC SYSTEM          |
|    (Dedicated Local Machine)       |          |     (UMass Amherst Cluster)        |
|                                    |          |                                    |
| • Broker Connection & Reconciliation|          | • Model Training (GPU/CPU)         |
| • Real-Time Market Data Stream     |          | • Large-Scale Walk-Forward Backtests|
| • Live Execution & Order Routing   |   SSH    | • High-Dim Feature Ablation Sweeps |
| • Hard Deterministic Risk Vetoes   | -------> | • 100k-Path Monte Carlo Engine     |
| • Real-Time P&L & Exposure Tracking|  (Async) | • Research Embeddings & RAG Corpus |
| • Workstation UI & Copilot Query   |          | • Domain LLM Fine-Tuning (QLoRA)   |
| • Final Model Promotion Governance | <------- | • Batch Inference & Sweeps         |
+------------------------------------+ Artifacts+------------------------------------+
```

**Crucial Invariant**: Unity must **never** become a required dependency for live trading safety.
- If the Unity cluster is offline, scheduled for maintenance, or network-partitioned, **live trading continues uninterrupted and safely** under local risk controls and kill-switch protections.
- The Unity client and Slurm jobs possess **zero broker execution authority**, **zero live capital authority**, and **zero ability to mutate live configuration files**.

---

## 2. Remote Layout & Environment Configuration

### Target Workspace
- **Remote Cluster Root**: `/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM`
- **Subdirectories**:
  - `src/`: Replicated Moneymaker research package.
  - `scripts/`: Python executable entrypoints.
  - `jobs/`: Slurm batch submission scripts (`*.slurm`).
  - `data/`: Immutable research dataset snapshots and manifests.
  - `logs/`: Slurm stdout/stderr logs (`%j.out`, `%j.err`).
  - `outputs/`: Checkpoints, metrics, prediction ledgers, artifacts.
  - `configs/`: Immutable experiment configuration JSONs.

### Shared Resources & Zero-Copy Reuse
1. **Pre-Cached Base Model**:
   - Path: `/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8/`
   - Cross-mount readable directly from `/scratch3/` with zero 52GB duplicate disk copy.
2. **Pre-Configured Conda Environment**:
   - Path: `/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice`
   - Pre-installed with `torch`, `transformers`, `accelerate`, `bitsandbytes`, `peft`, and `triton`.

---

## 3. Remote Job Management Utility Scripts

All remote operations are encapsulated in `scripts/unity/`:
- `submit_job.sh <slurm_script>`: Submits a Slurm job via SSH `sbatch`.
- `sync_to_unity.sh`: Synchronizes local research code and datasets to cluster via `rsync`.
- `sync_from_unity.sh`: Retrieves research outputs, metrics, and checkpoints back to local storage.
- `check_job.sh <job_id>`: Inspects real-time job status via `squeue`.
- `cancel_job.sh <job_id>`: Cancels a running or queued job via `scancel`.
- `bootstrap_env.sh`: Verifies conda and model cache access on the cluster.

---

## 4. Hardware Profiles & Slurm Partitions

| Workload Type | Slurm Template | Partition | Typical Hardware | Target Use Case |
|---|---|---|---|---|
| **GPU Model Training** | `jobs/gpu_training.slurm` | `uri-gpu` | 1x NVIDIA GPU, 8 CPUs, 64GB RAM | XGBoost GPU, PyTorch Deep Learning |
| **LLM Domain Fine-Tuning** | `jobs/llm_finetune.slurm` | `uri-gpu` | 1x NVIDIA A100/V100/L40S, 8 CPUs, 64GB RAM | Qwen 2.5 14B QLoRA / LoRA Training |
| **Parallel CPU Backtesting** | `jobs/cpu_backtest.slurm` | `uri-cpu` | 32 CPUs, 64GB RAM | Walk-forward cross-sectional backtests |
| **High-Memory Analytics** | `jobs/large_memory.slurm` | `large-mem` | 16 CPUs, 128GB RAM | Large cross-sectional covariance matrices |
| **Monte Carlo Risk Engine** | `jobs/monte_carlo.slurm` | `uri-cpu` | 32 CPUs, 64GB RAM | 100,000 path block bootstrap simulations |
| **Embedding Generation** | `jobs/embedding_generation.slurm` | `uri-gpu` | 1x GPU, 4 CPUs, 32GB RAM | Institutional memory semantic indexing |
