# Alpha B Data Contract & Feature Invariants

## 1. Input Data Specification
Alpha B utilizes daily adjusted OHLCV bar data with synchronized market and sector benchmark feeds:

```
Required Fields:
- timestamp: datetime (UTC, normalized to 16:00 ET market close)
- symbol: string (ticker identifier)
- open: float64 (adjusted)
- high: float64 (adjusted)
- low: float64 (adjusted)
- close: float64 (adjusted)
- volume: float64 (daily total volume)
- benchmark_close: float64 (e.g. SPY close for market-relative adjustments)
```

---

## 2. Feature Definitions & Calculation Invariants

All features are calculated using point-in-time data available at $T_{\text{close}}$ on day $t$. Forward-looking shifts or unadjusted historical adjustments are strictly prohibited.

| Feature Identifier | Formula / Definition | Lookback Window | Purpose |
| :--- | :--- | :--- | :--- |
| `ret_1d` | $(C_t - C_{t-1}) / C_{t-1}$ | 1 day | Shortest-term return shock |
| `ret_3d` | $(C_t - C_{t-3}) / C_{t-3}$ | 3 days | Intermediate return stretch |
| `reversal_3d` | $-(C_t - C_{t-3}) / C_{t-3}$ | 3 days | Core mean-reversion feature |
| `overnight_gap` | $(O_t - C_{t-1}) / C_{t-1}$ | 1 day | Overnight opening gap magnitude |
| `dist_sma20` | $(C_t - \text{SMA}_{20}(C)) / \text{SMA}_{20}(C)$ | 20 days | Trend extension measure |
| `vol_20d` | $\text{Std}(\Delta \ln C)_{20} \times \sqrt{252}$ | 20 days | Realized historical volatility |
| `volume_shock` | $V_t / \text{SMA}_{20}(V)$ | 20 days | Abnormal trading activity |
| `rel_strength_3d`| $\text{ret\_3d}_{\text{symbol}} - \text{ret\_3d}_{\text{SPY}}$ | 3 days | Market-relative idiosyncratic move |

---

## 3. Data Leakage Prevention Guarantees

1. **Available Timestamp Verification**: Features generated at close of day $t$ can only be used to predict returns starting from open/close of day $t+1$.
2. **Standardization & Scaling**: Rolling Z-scores and scalers are fitted strictly on trailing windows without future information leakage.
3. **Purged Walk-Forward Alignment**: Multi-day target labels require purging of overlapping forward return windows during model training.
