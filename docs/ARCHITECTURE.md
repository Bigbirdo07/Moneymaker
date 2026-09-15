# System Architecture

## Logical Architecture
```
MARKET DATA (OHLCV, Spreads, Benchmarks)
   │
   ▼
DATA QUALITY & VALIDATION LAYER (Schema, Timezone, Session Awareness, Anomaly Checks)
   │
   ▼
FEATURE STORE & PIPELINE (Returns, Momentum, Volatility, Volume, Relative Alpha)
   │
   ├────────────────────────┐
   ▼                        ▼
ALPHA SIGNALS        MARKET REGIMES
   │                        │
   └───────────┬────────────┘
               │
               ▼
       SIGNAL GENERATOR / STRATEGY
               │
               ▼
       OPPORTUNITY RANKER (Future Phase)
               │
               ▼
       DETERMINISTIC RISK ENGINE (Veto / Sizing / Constraints)
               │
               ▼
       PAPER EXECUTION SIMULATOR (Spread + Slippage + Commissions)
               │
               ▼
       PORTFOLIO LEDGER & METRICS ENGINE
```

## Modularity & Layer Isolation
- `src/core/`: Common types, domain models, Pydantic configuration schemas, and structured logging.
- `src/data/`: Ingestion, market calendars (NYSE regular/pre/post sessions), schema enforcement, and rigorous data quality validation.
- `src/features/`: Mathematically validated indicator calculation with strict available timestamp tracking.
- `src/strategies/`: Strategy interfaces and baseline implementations (Always Cash, Buy & Hold, Random, Momentum, Mean Reversion).
- `src/backtest/`: Chronological bar-by-bar simulation with explicit transaction cost models.
- `src/evaluation/`: Performance tear-sheets, Sharpe, Sortino, Drawdown, Expectancy, and Markdown research reports.
