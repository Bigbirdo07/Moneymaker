# False Positive Cost & Opportunity Retention Analysis

## 1. Trade-Off Analysis
- **VETO_FALSE_POSITIVE_RATE**: 46.9% (Winning setups skipped due to event rules)
- **VETO_RISK_AVOIDANCE_RATE**: 53.1% (Severe loss setups prevented)
- **Selectivity Ratio**: The policy avoids $1.35\times$ more losing tail-risk setups than winning setups.

## 2. Policy Tuning Principles
- Dilution offerings use `REDUCE_RISK` (50% size) rather than full `VETO` to preserve partial upside while capping downside exposure.
- Binary earnings and halts remain strict `VETO` because single catastrophic gap losses exceed typical trade expectancy by $>10\times$.