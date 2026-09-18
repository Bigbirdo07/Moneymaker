# Deterministic Event Risk Policy Engine: Architectural Design

## 1. Architectural Role & Execution Pipeline
The **`EventRiskPolicy`** acts as a pre-authorization deterministic firewall sitting between cross-sectional quant ranking and the risk execution engine:

```
Dynamic Universe -> Liquidity Filter -> FastScanner -> V3 Ranking -> EVENT RISK POLICY -> Expected Net Edge -> Risk Engine -> Order/Cash
```

## 2. Core Operational Principle
> **Quantitative attractiveness does NOT override deterministic event risk.**

The LLM/MMRM may discover and structure unstructured news/filings, but **only the deterministic rule engine assigns the final policy action** (`ALLOW`, `WARN`, `REDUCE_RISK`, `VETO`).

## 3. Four Canonical Policy Actions
- **`ALLOW`**: No active event restrictions. Order sizing at 100%.
- **`WARN`**: Minor informative news present. Order permitted at 100% with audit logging.
- **`REDUCE_RISK`**: Secondary offering or medium legal risk. Order permitted with deterministic 50% capital reduction.
- **`VETO`**: Binary earnings, trading halts, FDA dates, M&A, or bankruptcy. New entries strictly prohibited.

## 4. Open Position Safety State Machine
- **`HOLD`**: Maintain active trade with standard stops.
- **`REDUCE`**: Scale down open exposure.
- **`EXIT`**: Orderly market close prior to event effect.
- **`FREEZE_NO_ACTION_IF_HALTED`**: If a stock is halted during an open trade, the engine records `POSITION_TRAPPED_BY_HALT` rather than fabricating impossible fills.