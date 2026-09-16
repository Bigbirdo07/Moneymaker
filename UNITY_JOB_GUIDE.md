# Moneymaker Unity HPC Job Execution Guide

This operational guide details how to launch, monitor, sync, and validate quantitative research jobs running on the UMass Amherst Unity cluster.

---

## 1. Quick Start Workflow

The research iteration loop operates across four steps:
```
[1. Local Edit & Config] 
       │
       ▼  (rsync push)
[2. ssh unity sbatch jobs/<job>.slurm]
       │
       ▼  (squeue & tail logs)
[3. Slurm Execution on Unity]
       │
       ▼  (rsync pull)
[4. Ingestion & Cryptographic Validation in Local Workstation]
```

---

## 2. Launching Jobs via CLI

### A. Submitting GPU Training Job
```bash
./scripts/unity/submit_job.sh jobs/gpu_training.slurm
```

### B. Submitting QLoRA LLM Fine-Tuning Job
```bash
./scripts/unity/submit_job.sh jobs/llm_finetune.slurm
```

### C. Submitting 100k-Path Monte Carlo Simulation
```bash
./scripts/unity/submit_job.sh jobs/monte_carlo.slurm
```

---

## 3. Monitoring & Job Inspection

### Check Active Jobs
```bash
./scripts/unity/check_job.sh
```

### Stream Live Job Logs
```bash
ssh unity "tail -f /scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/logs/gpu_train_*.out"
```

### Cancel a Job
```bash
./scripts/unity/cancel_job.sh <job_id>
```

---

## 4. Synchronizing Artifacts Back to Local Station

Once a job completes, sync research outputs:
```bash
./scripts/unity/sync_from_unity.sh
```
This transfers `outputs/` (including `metrics.json`, `manifest.json`, `environment.json`, and adapter checkpoints) to local storage for cryptographic hash verification.

---

## 5. Standard Output Deliverables of Every HPC Job

Every Slurm runner produces the following standard files inside `outputs/<experiment_id>/`:
1. `metrics.json`: Numeric results (Sharpe, Net Expectancy, Rank IC, Drawdown, etc.).
2. `manifest.json`: Cryptographic hashes of code commit, dataset, and config.
3. `environment.json`: Node hostname, GPU model, CUDA version, CPU count, RAM, and runtime duration.
4. `stdout.log` & `stderr.log`: Complete execution telemetry.
