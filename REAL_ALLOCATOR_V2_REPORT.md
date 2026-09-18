# Real-Market Capital Allocator V2 Specification Report

## 1. Capital Allocation Rules ($1,000 Portfolio)
- **Max Concurrent Positions**: 2 (concentrates capital to ~$450–$500 per trade rather than tiny $100 positions)
- **Max Capital per Trade**: 50% of available equity
- **Sizing Policy**: `VOLATILITY_ADJUSTED` (scales inversely with 15m realized volatility)
- **Cash Retention**: 5% minimum cash reserve ($50.00)
- **CASH Default**: 100% Cash when no candidate exceeds the minimum edge hurdle
