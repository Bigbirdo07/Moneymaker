# Real Transaction Cost & Microstructure Model Report

## 1. Cost Components (`ESTIMATED_EXECUTION_COST`)
- **Base Half-Spread**: 2.5–3.5 bps on liquid canonical mega-caps (`AAPL`, `MSFT`, `NVDA`, `SPY`)
- **Slippage Proxy**: 1.5 bps baseline with participation-rate square-root penalty
- **Brokerage / Regulatory Proxy**: $0.0005/share (0.2–0.5 bps)
- **Total Round-Trip Friction**: **~6.50 bps** for normal liquid market hours
