# Moneymaker LLM Training Dataset Specifications (`DS_MM_LLM_V1`)

## 1. Overview & Pedagogical Objective

The `DS_MM_LLM_V1` dataset (`src/research/llm_dataset_builder.py`) contains structured instruction-tuning pairs designed for domain adaptation of open-source base LLMs (specifically **Qwen 2.5 14B Instruct**) into the **Moneymaker Research Model** (`MMRM-0.1`).

The goal is to teach:
- Strict quantitative reasoning and hypothesis formulation.
- Accurate trade explanations grounded in validated signals.
- Rigid adherence to data provenance and anti-hallucination standards.
- Exact tool selection from the 28-tool read-only Copilot interface.
- Respect for hard deterministic safety barriers and broker firewalls.

---

## 2. Dataset Categories & Taxonomy

The dataset is divided across 10 specialized categories:

| Category | Identifier | Description & Focus Area |
|---|---|---|
| **A. Quantitative Reasoning** | `QUANT_REASONING` | Expectancy calculations, Sharpe ratio deflation, t-statistics, p-values, friction drag analysis. |
| **B. Trade Explanations** | `TRADE_EXPLANATIONS` | Detailed breakdowns of entry/exit decisions, spread capture, momentum vs. mean-reversion edge. |
| **C. Strategy Diagnostics** | `STRATEGY_DIAGNOSTICS` | Alpha A / Alpha B health metrics, hit rate decay, slippage growth, signal correlation. |
| **D. Risk Diagnostics** | `RISK_DIAGNOSTICS` | VaR / Expected Shortfall 95/99%, sector concentration, portfolio beta, drawdown telemetry. |
| **E. Capacity Analysis** | `CAPACITY_ANALYSIS` | Market impact curves, ADV participation limits, capacity hold thresholds ($10k Alpha A, $5k Alpha B). |
| **F. Portfolio Reasoning** | `PORTFOLIO_REASONING` | Cross-strategy diversification, correlation matrix (-0.031), risk parity allocations. |
| **G. Experiment Review** | `EXPERIMENT_REVIEW` | Analysis of Slurm backtest metrics, walk-forward degradation, and parameter sensitivity. |
| **H. Leakage Identification** | `LEAKAGE_IDENTIFICATION` | Detecting target leakage, lookahead bias, un-embargoed features, and overlapping labels. |
| **I. Overfitting Identification** | `OVERFITTING_IDENTIFICATION` | Detecting multiple testing penalties, p-hacking, regime overfitting, and fragile hyperparameters. |
| **J. Tool-Use & Tool Selection** | `TOOL_USE_EXAMPLES` | Mapping user questions to exact JSON function calls (`tool_name` + parameters). |

---

## 3. Training / Validation / Test Partitions

To ensure unbiased evaluation:
- **Train Set (70%)**: 700 instruction-response examples across all 10 domains.
- **Validation Set (15%)**: 150 examples used for early stopping and LoRA hyperparameter tuning.
- **Held-Out Test Set (15%)**: 150 strictly unseen examples representing independent strategy variants, novel market regimes, and complex composite tool queries.
- **Final Benchmark Shield**: The `MONEYMAKER_LLM_BENCHMARK_V1` benchmark suite is **never** included in training or validation splits.
