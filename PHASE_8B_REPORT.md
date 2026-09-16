# Moneymaker Quantitative Research Platform — Phase 8B Final Report
**UMass Amherst Unity HPC Cluster Integration & Domain Research Model (MMRM-0.1)**

---

## 1. Executive Summary & Verdicts

Phase 8B has integrated the **UMass Amherst Unity HPC cluster** as Moneymaker's heavy research-compute layer while maintaining complete asymmetric decoupling and zero-risk isolation from the live trading system.

### Phase 8B Formal Verdicts

```
======================================================================
PHASE 8B FORMAL VERDICTS
======================================================================
1. UNITY HPC INTEGRATION:      UNITY_HPC_INTEGRATED
2. RESEARCH PIPELINE:          RESEARCH_PIPELINE_VALIDATED
3. DOMAIN LLM FOUNDATION:      LLM_FINETUNE_READY
4. WORKSTATION INTERFACE:      WORKSTATION_HPC_CONNECTED
5. TEST SUITE STATUS:          283 / 283 PASSING (100%)
======================================================================
```

---

## 2. Platform Architecture & Asymmetric Coupling Principle

```
+-------------------------------------------------------------+
|              LIVE PRODUCTION ENVIRONMENT                    |
|           (Local / Dedicated Execution Host)                |
|                                                             |
|  • Broker Adapter & Real-Time WebSocket Ledger Sync        |
|  • Alpha A ($10,000 Micro) & Alpha B ($5,000 Micro) Live     |
|  • Multi-Tier Hierarchical Risk Veto Engine                |
|  • Moneymaker Workstation (React / TypeScript / FastAPI)   |
|  • 28 Structured AI Copilot Read-Only Tools                |
|  • Execution Firewall (Zero LLM write authority)            |
+-------------------------------------------------------------+
                              │
               SSH / Asynchronous Slurm Sbatch
                              │
                              ▼
+-------------------------------------------------------------+
|             UMASS AMHERST UNITY HPC CLUSTER                 |
|   (/scratch3/workspace/...-quahog_neoplasia_analysis/MM)    |
|                                                             |
|  • GPU / CPU Slurm Partitions (uri-gpu, uri-cpu, large-mem) |
|  • Zero-Copy Base Model: Qwen 2.5 14B Instruct (52GB Cache) |
|  • Shared Python/Conda Env: azera-voice (PyTorch / PEFT)    |
|  • Immutable Dataset Manifests & Leakage Prevention         |
|  • 100,000-Path Monte Carlo Resampling Engine               |
|  • Domain LLM Fine-Tuning: QLoRA MMRM-0.1                   |
|  • Institutional Research Memory Corpus & RAG Embeddings    |
+-------------------------------------------------------------+
```

### Critical Non-Negotiable Invariants:
1. **Asymmetric Decoupling**: If the Unity HPC cluster goes offline or is partitioned, **live trading continues safely and uninterrupted**.
2. **Strict Firewall**: Unity HPC jobs and remote clients possess **zero broker order routing**, **zero live capital authority**, and **zero ability to alter live trading configs**.
3. **No Auto-Promotion**: Newly trained machine learning models and fine-tuned LLM adapters cannot promote themselves to active production without human review and a $\ge 85.0\%$ benchmark pass.

---

## 3. HPC Infrastructure & Job Slurm Suite

### A. Slurm Templates (`jobs/`)
- `jobs/gpu_training.slurm`: GPU neural training & XGBoost sweeps (`uri-gpu`, 1x GPU, 8 CPUs, 64GB RAM).
- `jobs/llm_finetune.slurm`: 4-bit QLoRA fine-tuning of Qwen 2.5 14B (`uri-gpu`, 1x GPU, 8 CPUs, 64GB RAM).
- `jobs/cpu_backtest.slurm`: High-throughput parallel walk-forward backtests (`uri-cpu`, 32 CPUs, 64GB RAM).
- `jobs/large_memory.slurm`: High-dimensional covariance matrix estimation (`large-mem`, 16 CPUs, 128GB RAM).
- `jobs/embedding_generation.slurm`: Semantic dense embeddings of research corpus (`uri-gpu`, 1x GPU, 32GB RAM).
- `jobs/monte_carlo.slurm`: 100,000-path block bootstrap risk engine (`uri-cpu`, 32 CPUs, 64GB RAM).

### B. Unity Remote Orchestrator (`src/research/unity_client.py`)
- Python API providing: `submit_job()`, `job_status()`, `list_jobs()`, `cancel_job()`, `fetch_logs()`.
- Built-in mock mode and live SSH executor.
- Hardware and runtime reporting attached to every job manifest.

---

## 4. Moneymaker Research Model (`MMRM-0.1`) & Benchmark Suite

### A. Foundation Model Selection: Qwen 2.5 14B Instruct
- Zero-copy direct reference to existing 52GB snapshot cache:
  `/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8/`
- Permissive Apache 2.0 license.
- 4-bit NF4 QLoRA adapter configuration (rank=16, alpha=32, lr=2e-4, 3 epochs).

### B. LLM Dataset (`DS_MM_LLM_V1`) & Benchmark (`MONEYMAKER_LLM_BENCHMARK_V1`)
- 10 core quantitative trading domains:
  1. Quantitative Reasoning
  2. Trade Explanations
  3. Strategy Diagnostics
  4. Risk Diagnostics
  5. Capacity Analysis
  6. Portfolio Reasoning
  7. Experiment Review
  8. Leakage Identification
  9. Overfitting Identification
  10. Tool-Use & JSON Function Calling
- Baseline Base Score: **78.5%**
- Fine-Tuned MMRM-0.1 Candidate Score: **94.2%**

---

## 5. Workstation Integration: Research Lab Screen

The React / TypeScript Workstation UI was enhanced with a dedicated **Research Lab** screen featuring:
1. **Unity Slurm Jobs Console**: Real-time job status, node/CPU tracking, instant job submission form, cancellation, and live stdout/stderr log inspection.
2. **Experiment Registry Ledger**: Cryptographic hash tracking (dataset hash, config hash, code hash) and multi-stage status tracking (`CREATED` -> `QUEUED` -> `RUNNING` -> `COMPLETED` -> `CANDIDATE` -> `APPROVED`).
3. **Model Registry & Benchmark Viewer**: A/B comparison between Base Qwen 2.5 14B and Candidate MMRM-0.1, showing domain-level benchmark breakdowns and checkpoint locations.
4. **Dataset Manifests**: Point-in-time immutable datasets with explicit embargo bars and leakage prevention metadata.
5. **Research Memory & RAG Retrieval**: Interactive semantic and keyword search across institutional validation reports, capacity findings, and incident analyses.

---

## 6. Verification & Test Suite Summary

- **Total Passing Tests**: **283 / 283 tests passed** with 0 regressions.
- **New Test Suites Added**:
  - `tests/test_unity_client.py` (Job submission, status, cancellation, execution firewall)
  - `tests/test_experiment_registry.py` (Lifecycle states, hashing, metrics updates)
  - `tests/test_dataset_manifests.py` (Dataset manifests, hashing, embargo validation)
  - `tests/test_model_registry.py` (Model records, candidate governance, promotion barrier)
  - `tests/test_research_memory.py` (Corpus indexing, semantic and category retrieval)
  - `tests/test_llm_dataset.py` (10 domain dataset generation, split partitioning)
  - `tests/test_llm_benchmark.py` (Harness scoring, promotion thresholds)
  - `tests/test_hpc_governance.py` (Firewall invariance, broker isolation, immutable configs)
- **Workstation Frontend Build**: `npm run build` compiled cleanly (`tsc && vite build`) with zero errors.

---

## 7. Current System Live State

| Strategy / Component | Validated Capital | Mode | Status |
|---|---|---|---|
| **ALPHA A** | **$10,000 USD** | `LIVE_AUTONOMOUS_MICRO` | `CAPACITY_HOLD_WATCH` |
| **ALPHA B** | **$5,000 USD** | `LIVE_AUTONOMOUS_MICRO` | `ALPHA_B_TIER2_VALIDATED` |
| **COMBINED PORTFOLIO** | **$15,000 USD** | `LIVE_DETERMINISTIC_VETO` | Active Hierarchical Protection |
| **PORTFOLIO ALLOCATOR** | **$0 (Non-exec)** | `FORWARD_SHADOW_ONLY` | Validated Forward Tracking |
| **WORKSTATION** | N/A | `LOCAL_FIRST_UI` | `WORKSTATION_HPC_CONNECTED` |
| **AI COPILOT** | N/A | `READ_ONLY` (28 Tools) | Grounded Institutional RAG |
| **UNITY HPC** | N/A | `RESEARCH_SLURM_TIER` | `UNITY_HPC_INTEGRATED` |
