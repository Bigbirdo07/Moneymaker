# Deterministic Risk Policy

## Foundational Mandate
1. **Separation of Concerns**: Risk limits are strictly programmatic and deterministic. Models (statistical, ML, or LLM) have zero authority to override risk controls.
2. **Capital Constraints**:
   - Initial Virtual Capital: **$1,000 USD**
   - Maximum Position Size: **10.0%** ($100.00 on $1,000 portfolio)
   - Maximum Risk Per Trade: **1.0%** of equity ($10.00)
   - Maximum Daily Portfolio Loss: **3.0%** (Halts trading immediately for the remainder of the session)
   - Maximum Drawdown Circuit Breaker: **15.0%**
   - Maximum Concurrent Positions: **5**
3. **Execution Restrictions**:
   - Leverage: **0.0x** (No margin borrowing)
   - Shorting: **Disabled** (Long-only in V1)
   - Options / Derivatives: **Disabled**
   - Overnight Holding: **Disabled** in V1 (all positions liquidated prior to 16:00 ET close)
