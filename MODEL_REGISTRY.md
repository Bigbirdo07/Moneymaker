# Moneymaker Model Registry & Checkpoint Governance

## 1. Overview

The **Moneymaker Model Registry** (`src/research/model_registry.py`) manages all trained machine learning models, neural weights, and domain-specific LLM adapter checkpoints (`MMRM-0.1`).

---

## 2. Model Lifecycle States & Promotion Firewall

### Lifecycle States
1. `EXPERIMENTAL`: Newly trained weights or fine-tuned LoRA adapters under active evaluation.
2. `CANDIDATE`: Completed benchmark evaluation; met baseline accuracy and safety criteria.
3. `VALIDATED`: Approved by human governance for workstation copilot advisory queries.
4. `REJECTED`: Failed benchmark score, exhibited hallucinations, or showed provenance errors.
5. `ARCHIVED`: Deprecated checkpoint superseded by newer versions.

### Strict Non-Auto-Promotion Invariant
```
+--------------------------+
|  Newly Trained Weights   |
|   (Unity QLoRA / Torch)  |
+--------------------------+
             │
             ▼
+--------------------------+
|  Benchmark Evaluation    |
|   (10 Domain Test Suite) |
+--------------------------+
             │
             ├─── Benchmark < 85.0% ───> [REJECTED]
             │
             ▼
+--------------------------+
|  Tool-Use & Safety Audit |
|   (Zero Broker Invariant)|
+--------------------------+
             │
             ├─── Attempted Broker Action ───> [FATAL REJECT]
             │
             ▼
+--------------------------+
| Human Governance Review  |
| (Manual Promotion Signoff|
+--------------------------+
             │
             ▼
+--------------------------+
| Workstation Active Copilot|
| (Advisory / Explanatory) |
+--------------------------+
```

**Critical Rule**: No fine-tuned LLM or quantitative model can automatically promote itself to active production. Promotion strictly requires:
- Overall benchmark score $\ge 85.0\%$.
- 100% pass on tool safety and broker execution firewall tests.
- Explicit manual confirmation in workstation settings.

---

## 3. Registered Model Inventory

| Model ID | Base Model | Method | Dataset | Benchmark Score | Approval State | Workstation State |
|---|---|---|---|---|---|---|
| `BASE-QWEN-2.5-14B` | Qwen2.5-14B-Instruct | Zero-shot Base | N/A | 78.5% | `VALIDATED` | **ACTIVE (Default)** |
| `MMRM-0.1-QLORA` | Qwen2.5-14B-Instruct | QLoRA (r=16, α=32) | `DS_MM_LLM_V1` | 94.2% | `CANDIDATE` | Evaluation Candidate |
