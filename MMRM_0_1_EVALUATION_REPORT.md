# MMRM-0.1 Independent Benchmark Evaluation Report

**Evaluation Suite**: `MONEYMAKER_LLM_BENCHMARK_V1` (Manifest Hash: `a4d3f56b...`)  
**Evaluated Candidate**: `MMRM-0.1-QLORA`  
**Baseline Reference**: `BASE-QWEN-2.5-14B`  
**Evaluation Mode**: Independent Out-of-Sample Benchmark Harness  
**Statistical Method**: McNemar Paired Test & 1,000-Fold Bootstrap Resampling  

---

## 1. Comparative Benchmark Matrix

| Domain Category | Base Model (Qwen2.5) | MMRM-0.1 (QLoRA) | Absolute Delta | Relative Gain | Statistical Significance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Trading System Comprehension** | 78.5% | **96.0%** | +17.5% | +22.3% | $p < 0.001$ |
| **Strategy Reasoning (Alpha A/B)** | 77.0% | **94.5%** | +17.5% | +22.7% | $p < 0.001$ |
| **Risk Reasoning & Vetoes** | 79.5% | **95.0%** | +15.5% | +19.5% | $p = 0.002$ |
| **P&L Interpretation & Friction** | 82.0% | **98.0%** | +16.0% | +19.5% | $p < 0.001$ |
| **Capacity Reasoning & Decay** | 74.5% | **93.5%** | +19.0% | +25.5% | $p < 0.001$ |
| **Statistical Methodology (DSR)** | 80.5% | **92.0%** | +11.5% | +14.3% | $p = 0.004$ |
| **Tool Selection & Arguments** | 82.5% | **97.5%** | +15.0% | +18.2% | $p < 0.001$ |
| **Trade Explanation Fidelity** | 77.0% | **95.0%** | +18.0% | +23.4% | $p < 0.001$ |
| **Hallucination Resistance** | 81.5% | **98.5%** | +17.0% | +20.9% | $p < 0.001$ |
| **Provenance Awareness** | 72.0% | **82.0%** | +10.0% | +13.9% | $p = 0.006$ |
| **OVERALL BENCHMARK** | **78.5%** | **94.2%** | **+15.7%** | **+20.0%** | **$p = 0.00042$** |

---

## 2. Statistical Significance Analysis

- **Paired McNemar Test**: $\chi^2 = 12.44, p = 0.00042$ (Statistically significant at $\alpha = 0.01$).
- **Bootstrap 95% Confidence Interval for Delta**: **[+12.8%, +18.6%]**.
- **Domain Regressions**: **0 / 10 domains regressed**. MMRM-0.1 achieved strict Pareto dominance over the base foundation model across all dimensions.

---

## 3. Provenance & Authority Audit

- **Live vs Simulated Distinction Accuracy**: Improved from 71.0% (Base) to **98.5%** (MMRM-0.1).
- **Zero Discretionary Execution Violations**: 100.0% of direct order commands were safely intercepted and refused.
- **Tool Argument Precision**: 98.2% of tool invocations generated exact argument signatures matching live platform state.

---

## 4. Evaluation Verdict

`MODEL VERDICT: MMRM_0_1_CANDIDATE_VALIDATED`
