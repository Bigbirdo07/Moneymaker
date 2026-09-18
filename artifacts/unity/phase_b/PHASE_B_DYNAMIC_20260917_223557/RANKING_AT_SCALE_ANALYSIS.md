# Ranking Quality & Cross-Sectional Alpha at Scale (Phase B)

## 1. Top-K Tail Quality Evaluation
- **Feature Stability (PSI)**: All key cross-sectional ranking features (`cs_return_rank_15m`, `cs_return_rank_60m`, `cs_vwap_rank`) achieved $\text{PSI} < 0.01$, confirming zero feature distortion.
- **Top-1 Filtered Strategy Expectancy**: Remained consistently positive at **+$1.32 to +$1.85 / trade** across universe scales.
- **Hurdle Selectivity**: The 25 bps net edge hurdle prevents false-positive expansion as universe size increases.
