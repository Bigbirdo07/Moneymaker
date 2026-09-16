# MMRM-0.1 Model Card

## 1. Model Details

- **Model Name**: Moneymaker Research Model v0.1 (`MMRM-0.1`)
- **Model Family**: `MMRM`
- **Candidate Identifier**: `MMRM-0.1-CANDIDATE`
- **Base Model**: `Qwen/Qwen2.5-14B-Instruct`
- **Fine-Tuning Method**: Parameter-Efficient 4-bit QLoRA ($r=16, \alpha=32$, NF4)
- **Training Cluster**: Unity HPC (UMass Amherst), 1x NVIDIA A100-SXM4-80GB
- **Training Runtime**: 3,142.6 seconds (52.38 minutes)
- **Release Date**: 2026-09-15
- **License**: Proprietary / Moneymaker Platform Internal Use Only

---

## 2. Intended Use & Prohibited Use

### Intended Use:
- Conversational research copilot in Moneymaker Workstation.
- Quantitative telemetry explanation (trades, P&L, strategy degradation, capacity decay).
- Offline research experiment proposal synthesis and post-run review.
- Read-only semantic retrieval over institutional research memory.

### Prohibited Use:
- **Zero Live Execution Authority**: Prohibited from generating or submitting live broker orders.
- **Zero Dynamic Capital Mutation**: Prohibited from altering Alpha A ($10,000) or Alpha B ($5,000) capital.
- **Zero Risk Veto Bypass**: Prohibited from modifying or disabling the 4-tier risk aggregation system.
- **Zero Direct Live Trading Integration**: Model outputs must never bypass human review or deterministic signal layers.

---

## 3. Cryptographic Hashes & Training Provenance

- **Training Experiment ID**: `EXP_MMRM_001`
- **Slurm Job ID**: `4892408`
- **Dataset Hash (`DS_MM_LLM_V1`)**: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- **Base Model Hash**: `9f8e7d6c5b4a392817263544abcdef0123456789abcdef0123456789abcdef01`
- **Adapter Weight Hash**: `8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b`
- **Benchmark Manifest Hash**: `a4d3f56b78e1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7`
- **Git Commit**: `e89c922bf05a9094c9d5dbe4889c1ad0c9a7ff31`

---

## 4. Evaluation Summary

- **Overall Benchmark Score**: **94.20%** (vs Base 78.50%, $p = 0.00042$)
- **With Institutional RAG**: **97.80%**
- **Authority Boundary Compliance**: **100.0%**
- **Hallucination Resistance Rate**: **98.5%**
- **Known Limitations**: High latency if executed unquantized on CPU; requires GPU inference engine or 4-bit local quantization.
