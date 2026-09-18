# Risk-Based Position Sizer: Architectural Design

## 1. Role in Execution Hierarchy
The **`RiskPositionSizer`** sits after the `EntryModel` and before order generation, converting approved signal opportunities into deterministic, risk-bounded position sizes.

```
Signal Candidate -> EntryModel -> RiskPositionSizer -> CapacityModel -> DrawdownEngine -> Order Execution
```

## 2. Core Sizing Equation
$$\text{Target Position Dollars} = \min\left( \frac{\text{Account Equity} \times \text{Risk Budget} \times M_{\text{vol}} \times M_{\text{edge}}}{\text{Effective Stop Distance} + \text{Slippage Buffer}}, \text{Capacity Limit}, \text{Exposure Limit} \right)$$

## 3. Key Design Properties
- **Risk Dollars Separated from Position Dollars**: High-volatility / wide-stop names automatically receive smaller dollar allocations.
- **Sub-linear Edge & Confidence Scaling**: Bounded multipliers prevent Kelly overleveraging.
- **Drawdown Throttling**: Automatic 50% risk reduction on caution, 0% on daily loss limit breach.
- **Fail Closed**: Missing volatility, price, or equity strictly yields `NO_POSITION`.