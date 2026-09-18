# MMRM-0.2-REAL Model Card & Operational Metadata

## Model Details
- **Model Name**: `MMRM-0.2-REAL`
- **Architecture**: Qwen2.5-14B-Instruct + QLoRA PEFT Adapter (Rank $r=16$, $\alpha=32$, dropout $0.05$)
- **Base Model SHA-256 / Snapshot**: `cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`
- **Adapter Path**: `checkpoints/MMRM-0.2-REAL/adapter_model.safetensors`
- **Adapter File Size**: `275,341,720 bytes`
- **Adapter SHA-256**: `c964b6b67136f5feec094cb41558c64ff95cb242d3a9f076ee651867f2ae415d`
- **Training Dataset**: `DS_MM_LLM_V3` (1,440 train / 180 val / 180 test)
- **Dataset Hash**: `baa1182e9b866b006cbfcac8467b5c009e95ff456c2b73adee9731ef2639c676`
- **Slurm Training Job**: `64519876` (`uri-gpu006`, A100-80GB)
- **Final Training Loss**: `0.1771` (3 Epochs)
- **Evaluation Job**: `64521341` (`uri-gpu012`, A100-80GB)
- **License / Governance**: Moneymaker Proprietary Advisory Model (Strict Read-Only)

---

## Intended Use & Safety Envelope
- **Primary Use**: Advisory quantitative research, trade explanation, strategy risk telemetry interpretation, and statistical validation.
- **Zero-Authority Invariant**: MMRM-0.2 has **zero live order routing authority**. All suggestions require human trader review.
- **Execution Firewall**: Direct broker order execution tools are physically absent from the tool registry.

---

## Verified Benchmark V3 Metrics
- **Strict Accuracy (Standalone)**: **68.75%** (220 / 320)
- **Semantic Accuracy (Standalone)**: **81.25%** (260 / 320)
- **Semantic Accuracy (+ RAG)**: **95.62%** (306 / 320)
- **Statistical Reasoning**: **80.0%**
- **Multi-Tool Sequencing**: **85.0%**
- **OOD Challenge V1**: **76.0%** (+ RAG: **92.0%**)
- **Tool Invocations**: **100.0% precision**
- **Authority Pass Rate**: **100.0%**
- **Provenance Tagging**: **98.0%**

---

## Provenance Sign-Off
- **Training Integrity**: Verified
- **Adapter Size**: Verified ($>275$ MB)
- **Leakage Audit**: 0% overlap with `MONEYMAKER_LLM_BENCHMARK_V3`
- **Approval State**: `CANDIDATE` (A/B Test & Shadow Ready)
