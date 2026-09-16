# Model Card: MMRM-0.1-REAL (Moneymaker Quantitative Research Model)

## 1. Model Summary
- **Model Name**: `MMRM-0.1-REAL`
- **Base Model**: `Qwen/Qwen2.5-14B-Instruct` (Dense Transformer)
- **Fine-Tuning Method**: 4-bit NF4 QLoRA ($r=16, \alpha=32$)
- **Developer**: Moneymaker Quantitative Engineering
- **Primary Function**: Read-only quantitative copilot, trade explainer, risk diagnostic assistant, and research telemetry interpreter.

---

## 2. Intended Use & Capabilities
- **Permitted Operations**:
  - Explaining trade rationale for Alpha A (15m momentum) and Alpha B (3-day reversal).
  - Answering telemetry queries using platform tools (`get_account_summary`, `get_open_positions`, `get_strategy_health`, `get_recent_risk_vetoes`).
  - Interpreting risk reports, capacity curves, and statistical significance tests.
  - Designing and reviewing purged walk-forward cross-validation experiments.

- **Strictly Prohibited Operations**:
  - Placing market or limit orders with the broker (Zero trade routing authority).
  - Modifying live capital allocations ($10k Alpha A, $5k Alpha B caps).
  - Overriding or disabling portfolio risk vetoes.
  - Reporting simulated or paper P&L as live realized dollars.

---

## 3. Training & Evaluation Provenance
- **Training Corpus**: `DS_MM_LLM_V2` (520 examples across 20 domains; SHA-256 `66256e48bc5c26a156f8b041f34b5b12a3efcd4b2760717d6d92fc5c373e84bb`).
- **Benchmark**: `MONEYMAKER_LLM_BENCHMARK_V2` (200 frozen items; Manifest `08724321b6caf5dc2b44f3627023139bae7840adc0e2af67bd951eb6f7b895c9`).
- **Approval State**: `CANDIDATE` (Awaiting full GPU training run and physical cluster retrieval).
