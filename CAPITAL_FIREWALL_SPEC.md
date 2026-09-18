# Capital Firewall Specification & Strategy Ledger (Phases F7, F8)

## 1. Proving Stage Constraint
- **Authorized Capital**: **$1,000.00**
- **Capital Tier**: `TIER_PAPER_1000`
- **Max Open Positions**: **1**
- **Max Position Exposure**: **75.0% ($750.00)**
- **Max Risk per Trade**: **0.75% ($7.50)**

## 2. Broker Balance Decoupling
Default broker paper account balances (e.g. $100,000.00) are explicitly ignored by the `StrategyCapitalLedger`.
