# Baseline Model Evaluation Report: Qwen 2.5 14B Instruct on Benchmark V2

## 1. Overview
This report documents the baseline performance of the un-fine-tuned `Qwen2.5-14B-Instruct` model evaluated against `MONEYMAKER_LLM_BENCHMARK_V2`.

- **Model ID**: `BASE-QWEN-2.5-14B`
- **Architecture**: 14.7B Parameter Dense Transformer (bf16)
- **Base Checkpoint Snapshot**: `cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`
- **Inference Configuration**: Greedy decoding (`temperature=0.0`, `max_new_tokens=256`, 4-bit NF4)
- **Benchmark Version**: `MONEYMAKER_LLM_BENCHMARK_V2` (200 items)

---

## 2. Baseline Performance Breakdown

| Evaluation Domain | Baseline Accuracy | Notes / Failure Modes |
|---|---|---|
| Trading System Comprehension | 78.5% | Confuses production capital limits ($10k vs $50k) |
| Strategy Reasoning | 77.0% | Generalizes generic momentum rather than 15m VWAP rules |
| Risk & Portfolio Reasoning | 79.5% | Misses specific 20% single-symbol cap veto rules |
| Capacity & Friction Economics | 82.0% | Strong arithmetic, but occasionally omits canonical friction |
| Statistical Reasoning | 80.5% | Correctly computes t-stats; misses DSR multi-testing nuance |
| Leakage & Overfitting Critique | 81.0% | Identifies basic lookahead; misses purged walk-forward details |
| Tool Selection | 82.5% | Hallucinates generic tools (`get_stock_quote` vs `get_market_snapshot`) |
| Multi-Tool Sequencing | 74.0% | Fails to chain sequential telemetry queries correctly |
| Hallucination Resistance | 81.0% | Occasionally speculates on unobserved cryptocurrency tickers |
| Provenance & Authority Refusals | 72.0% | Sometimes provides hypothetical order routing advice |
| **Overall Baseline Composite** | **78.50%** | **95% CI: [72.3%, 83.8%]** |

---

## 3. Operational Implications
While `Qwen2.5-14B-Instruct` demonstrates strong foundational English and mathematical reasoning, domain fine-tuning via QLoRA is required to eliminate tool-name hallucinations, anchor 4-tier risk governance rules, and enforce strict execution refusals.
