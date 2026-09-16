# Baseline Evaluation Report: Qwen2.5-14B-Instruct

**Experiment ID**: `EXP_BASE_EVAL_001`  
**Slurm Job ID**: `4892011`  
**Target Foundation Model**: `Qwen2.5-14B-Instruct` (Un-fine-tuned)  
**Cluster / Hardware**: Unity HPC — 1x NVIDIA A100-SXM4-80GB  
**Runtime**: 418.5 seconds  
**Git Commit**: `e89c922bf05a9094c9d5dbe4889c1ad0c9a7ff31`  
**Benchmark Version**: `MONEYMAKER_LLM_BENCHMARK_V1`  

---

## 1. Executive Summary

The base pretrained candidate `Qwen2.5-14B-Instruct` was evaluated on Unity HPC across the 10 frozen evaluation domains without domain fine-tuning or specialized prompts. While general reasoning and syntax compliance were acceptable, the base model exhibited notable weaknesses in Moneymaker-specific institutional knowledge, capacity degradation mathematics, multi-day cohort lifecycles, and distinguishing simulated vs live evidence.

- **Overall Benchmark Score**: **78.50%**
- **95% Bootstrap Confidence Interval**: **[75.8%, 81.2%]**
- **Authority Boundary Compliance**: **100.0%** (Correctly refuses direct trades due to general alignment)
- **Provenance Awareness**: **71.0%** (Frequently confuses backtest logs with live broker telemetry)
- **Hallucination Resistance**: **81.5%** (Tends to speculate on unknown ticker metrics instead of asserting absence of evidence)

---

## 2. Domain-by-Domain Performance Breakdown

| Evaluation Domain | Base Model Score | Target Threshold | Baseline Verdict |
| :--- | :--- | :--- | :--- |
| **Trading System Comprehension** | 78.5% | 90.0% | Below Target |
| **Strategy Reasoning** | 77.0% | 90.0% | Below Target |
| **Risk Reasoning** | 79.5% | 90.0% | Below Target |
| **P&L Interpretation** | 82.0% | 95.0% | Moderate |
| **Capacity Reasoning** | 74.5% | 90.0% | Severe Deficit |
| **Statistical Reasoning** | 80.5% | 90.0% | Moderate |
| **Tool Selection** | 82.5% | 95.0% | Moderate |
| **Trade Explanation** | 77.0% | 90.0% | Below Target |
| **Hallucination Resistance** | 81.5% | 95.0% | Vulnerable |
| **Provenance Awareness** | 72.0% | 95.0% | Severe Deficit |
| **AGGREGATE AVERAGE** | **78.5%** | **90.0%** | **BASELINE BENCHMARK** |

---

## 3. Observed Failure Modes in Base Model

1. **Capacity Nuance Deficiency**:
   - The base model failed to recognize that Alpha A's frozen status at $10k is governed by empirical edge retention (70.70%) and market impact friction, mistakenly assuming it was an arbitrary human risk choice.
2. **Provenance Conflation**:
   - When asked about historical returns, base Qwen referenced general theoretical formulas without citing Moneymaker's `BROKER_LIVE` or `FORWARD_SHADOW` badges.
3. **Tool Parameter Sub-optimality**:
   - On queries like *"Why did we buy AMD?"*, the base model frequently chose general trade history (`get_trade_history`) rather than targeted trade explanation (`explain_trade`).

---

## 4. Conclusion & Fine-Tuning Mandate

Pretrained general LLMs lack the domain-specific ontology, friction equations, and institutional guardrails required for high-fidelity quantitative research assistance. QLoRA fine-tuning on `DS_MM_LLM_V1` is empirically justified.
