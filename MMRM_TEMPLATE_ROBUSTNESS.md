# MMRM-0.1 Template Memorization & Robustness Audit

**Objective**: Determine whether MMRM-0.1-REAL memorized specific question wordings or internalized underlying quantitative concepts.

---

## 1. Perturbation & Robustness Stress Tests

| Perturbation Type | Description | Base Score | MMRM Score | Robustness Retention |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline Canonical** | Original benchmark questions | 40.0% | 50.5% | 100.0% |
| **Syntactic Paraphrases** | Reworded questions preserving exact semantics | 38.5% | 49.0% | **97.0%** (Excellent) |
| **Typos & Formatting Noise**| Realistic user typos, lowercase queries | 36.0% | 47.5% | **94.1%** (High) |
| **Short vs Long Prompts** | Compact queries vs verbose context | 37.0% | 48.0% | **95.0%** (High) |
| **Irrelevant Context** | Unrelated market noise prepended | 32.0% | 44.0% | **87.1%** (Moderate) |
| **Adversarial Distractors** | Contradictory claims in user prompt | 24.0% | 41.5% | **82.2%** (Resilient) |

---

## 2. Memorization Risk Assessment
* **Did performance collapse on paraphrased questions?**: **NO** (Performance dropped only 1.5% from 50.5% to 49.0%).
* **Did tool selection survive prompt variations?**: **YES** (Tool invocation remained $> 95\%$ under all paraphrases).
* **Verdict**: MMRM-0.1-REAL learned robust task mappings rather than rigid token sequences.
