# Paper Trading Runtime Architecture (Phase F1)

## 1. System Overview
The Moneymaker Paper Trading Runtime connects all quantitative research and risk management layers into an autonomous forward execution machine operating strictly in `ExecutionEnvironment.PAPER`.

## 2. Complete End-to-End Operating Cycle
```mermaid
flowchart TD
    A[08:00 Premarket Quotes] --> B[MorningBriefService]
    B --> C[MarketRegime & SessionGate]
    C --> D[09:30 Market Open]
    D --> E[Real-Time FastScanner 1m]
    E --> F[CrossSectionalRanker]
    F --> G[EventRiskPolicy Firewall]
    G --> H[ExpectedExecutionCost]
    H --> I[RiskPositionSizer]
    I --> J[ExecutionAuthorization]
    J --> K[OrderIntent Generator]
    K --> L[AlpacaPaperBrokerAdapter]
    L --> M[Continuous Position Monitoring]
    M --> N[15:45 Automated EOD Flatten]
    N --> O[16:00 Broker Reconciliation]
    O --> P[Post-Close Journal]
```

## 3. Core Safety Invariants
1. **Absolute Real-Money Firewall**: Any execution mode other than `PAPER` or `SIMULATION` raises `RealMoneyAuthorizationError`.
2. **Strategy Capital Ledger**: Position sizes and exposure ceilings derive strictly from authorized proving capital ($1,000.00).
3. **Idempotent Order Intents**: Unique cryptographic `order_intent_id` prevents duplicate submissions.
4. **Automated EOD Flattening**: Flattening window (15:45-15:55 ET) ensures zero overnight equity risk.
