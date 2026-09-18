# Position Rounding & Share Calculation Analysis

## 1. Share Precision Impact
- On small accounts ($1,000), whole-share rounding introduces discrete cash residuals on high-priced stocks (e.g. $200+ shares).
- The engine computes exact actual notional and risk dollars post-rounding to avoid underestimating risk.