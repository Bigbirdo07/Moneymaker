# Forward Evidence Classification & Anti-Fabrication Policy (Phases F41, F81)

## 1. Evidence Hierarchy
1. `REAL_HISTORICAL_MARKET_DATA`: Walk-forward backtests on past market tape.
2. `SIMULATED_EXECUTION_ON_REAL_MARKET_DATA`: Offline replay with simulated broker.
3. `FORWARD_PAPER_TRADING`: Genuinely forward, unseen live paper market sessions.

## 2. Zero Fabrication Invariant
Simulated or back-filled trades must **never** be labeled `FORWARD_PAPER_TRADING`. Only live forward sessions connected to paper brokers earn this classification.
