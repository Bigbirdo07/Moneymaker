# Known Limitations & Research Constraints (Phase 1)

1. **Market Impact Non-Linearity**:
   - The current cost model uses linear basis points and simple volume participation penalty. It does not model full Almgren-Chriss square-root impact or limit order book queue dynamics.
2. **5-Minute Discrete Bars**:
   - Intrabar price paths are approximated via High/Low extremes for stop/target checks. Sub-minute order-flow and queue priority are not simulated.
3. **Synthetic Historical Testing**:
   - Phase 1 validation includes high-fidelity synthetic GBM + U-curve datasets alongside historical loader interfaces. Live streaming broker integration is reserved for later phases.
4. **Universe Constrained to Liquid Large Caps**:
   - Alpha models calibrated on large-cap equities (SPY, AAPL, MSFT) must not be assumed to generalize to illiquid small-caps.
