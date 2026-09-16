# UMass Amherst Unity HPC Cluster Environment Audit

## 1. Executive Summary & Cluster Topography
This audit establishes the formal infrastructure profile of the **UMass Amherst Unity HPC Cluster** integration for the Moneymaker Quantitative Research Platform. Unity serves as the asynchronous heavy research-compute layer (model training, walk-forward simulations, Monte Carlo risk engines, and LLM fine-tuning), completely decoupled from local live execution.

---

## 2. Cluster Pathing & Mount Architecture

| Resource | Canonical Cluster Path | Description / Access Rules |
| :--- | :--- | :--- |
| **Moneymaker HPC Root** | `/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/` | Primary project root for code, scripts, data, logs, outputs. |
| **Shared Model Cache** | `/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/` | Direct cross-mount read access (zero copy required). |
| **Target LLM Weights** | `.../models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8/` | Qwen 2.5 14B Instruct base model weights (52 GB). |
| **Shared Conda Env** | `/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice/` | PyTorch, Hugging Face Transformers, Accelerate, BitsAndBytes. |

---

## 3. Slurm Partitions & Compute Specifications

| Partition | Resource Type | Typical Allocation | Max Walltime | Primary Compute Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **`uri-gpu`** | NVIDIA GPU (A100 / L40S / RTX8000) | 1 GPU, 8 CPUs, 64 GB RAM | 04:00:00 - 24:00:00 | QLoRA / LoRA fine-tuning, embeddings, XGBoost GPU sweeps. |
| **`uri-cpu` / `cpu`**| High-Density Multi-Core CPU | 16-64 CPUs, 64-128 GB RAM | 08:00:00 - 48:00:00 | Purged walk-forward backtests, Monte Carlo resampling. |
| **`highmem`** | High-Memory Node | 32 CPUs, 256-512 GB RAM | 12:00:00 | Cross-asset tick universe feature matrix assembly. |

---

## 4. Software Stack & Module Environment
- **Conda Environment Profile**: `~/miniconda3/etc/profile.d/conda.sh`
- **Active Environment**: `azera-voice` (Python 3.10+, PyTorch with CUDA 12.x support)
- **Key Installed Libraries**: `torch`, `transformers`, `accelerate`, `bitsandbytes`, `peft`, `scipy`, `numpy`, `pandas`, `xgboost`, `scikit-learn`.
- **Slurm Workload Manager**: Native Slurm job submission via `sbatch`, monitoring via `squeue`, log streaming via `tail -f`.

---

## 5. Security & Isolation Guarantee
1. **Zero Broker Keys on HPC**: Broker API keys, account numbers, and live execution credentials are never pushed to or stored on Unity.
2. **Asymmetric Network Flow**: Live trading is strictly independent. Unity downtime never degrades or halts local live market operations.
