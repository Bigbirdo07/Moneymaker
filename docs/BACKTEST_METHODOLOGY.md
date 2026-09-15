# Backtesting & Validation Methodology

## Chronological Simulation & Frictions
To ensure scientific validity and reproducibility, the backtesting engine follows these strict principles:

1. **Strict Chronological Evaluation**:
   - Time-series data is processed strictly in chronological order $t_0, t_1, \dots, t_N$.
   - Random K-Fold cross validation is strictly prohibited.
2. **Order Execution & Pricing Realism**:
   - Orders generated at bar $t$ are filled at the beginning of bar $t+1$ (or bar $t$ close if assumed simultaneous).
   - Execution price includes:
     - **Half-Spread**: $\text{Gross Price} \times \text{Half Spread Bps}$
     - **Slippage**: Base slippage (2.0 bps) + dynamic volume penalty if order size exceeds 1% of bar volume.
     - **Commissions**: Fixed or per-share fees deducted from net cash.
3. **Intraday Session Rules**:
   - Trading is constrained to regular hours ($09:30 - 16:00$ ET).
   - No new positions are initiated in the final 20 minutes of the session.
   - All open positions are forced flat in the final 10 minutes ($15:50$ ET) to prevent overnight gap risk.
4. **Mandatory Benchmark Comparison**:
   - Every backtest must be benchmarked against:
     - Always Cash (Zero-return, zero-volatility baseline)
     - Buy & Hold (Passive broad-market exposure)
     - Random Predictor (Hypothesis testing against pure noise)
