# Engine V3 Feature Engineering & Cross-Sectional Alpha Research Report

## 1. Feature Architecture Overview
Engine V3 introduces contemporaneous cross-sectional rankings and market breadth metrics across the 50-stock universe:
- `rel_strength_15m_bps`, `rel_strength_60m_bps`: Relative strength of each stock vs universe mean.
- `market_breadth_above_vwap`: Proportion of 50-stock universe trading above intraday VWAP.
- `cs_return_rank_15m`, `cs_return_rank_60m`: Percentile rankings within contemporaneous 15-minute time slices.
- `market_regime_tradable`: Binary Stage-1 market filter blocking long exposure during market-wide cascades.