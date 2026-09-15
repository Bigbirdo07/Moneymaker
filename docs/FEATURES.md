# Features & Target Documentation

## Feature Safety & Lookahead Prevention
Every feature row carries:
- `event_timestamp`: The start timestamp $t$ of the bar.
- `available_timestamp`: $t + \Delta t$ (e.g. $t + 5\text{min}$). No strategy, order, or signal may access bar $t$'s metrics before $t + \Delta t$.

## Feature Categories

### 1. Return Features (`src/features/returns.py`)
- `feature_return_1b`: 1-bar simple percentage return $\frac{C_t - C_{t-1}}{C_{t-1}}$
- `feature_return_3b`: 3-bar return (15m on 5m timeframe)
- `feature_return_6b`: 6-bar return (30m)
- `feature_return_12b`: 12-bar return (60m)
- `feature_log_return_1b`: 1-bar log return $\ln(C_t / C_{t-1})$

### 2. Momentum & Trend (`src/features/momentum.py`)
- `feature_rsi_14`: Wilder's 14-period Relative Strength Index
- `feature_macd_line`: Fast EMA (12) - Slow EMA (26) normalized by price
- `feature_macd_signal`: 9-period EMA of MACD line
- `feature_macd_hist`: MACD line - Signal line
- `feature_ema_9`, `feature_ema_21`, `feature_ema_50`: Exponential moving averages
- `feature_dist_ema_9`, `feature_dist_ema_21`: Relative distance from price to EMA
- `feature_ema_cross_9_21`: Spread between short and medium EMA

### 3. Volatility Features (`src/features/volatility.py`)
- `feature_realized_vol_20b`: 20-bar rolling standard deviation of log returns
- `feature_atr_14`: 14-period Average True Range
- `feature_atr_pct`: ATR normalized by price
- `feature_garman_klass_vol`: Range-based Garman-Klass volatility estimator
- `feature_bb_pct`: Position within Bollinger Bands $\frac{C_t - \text{Lower}}{\text{Upper} - \text{Lower}}$

### 4. Volume Features (`src/features/volume.py`)
- `feature_relative_volume_20b`: Volume relative to 20-bar rolling mean (RVOL)
- `feature_volume_zscore_20b`: 20-bar volume standard score
- `feature_vwap_deviation`: Relative price deviation from intraday VWAP
- `feature_price_volume_corr_5b`: Rolling correlation between return and volume

### 5. Research Targets (`target_*` columns)
*Strictly for model training and out-of-sample evaluation. Forbidden in production decision logic.*
- `target_future_return_3b`: Forward return over 15 minutes
- `target_future_return_6b`: Forward return over 30 minutes
- `target_future_return_12b`: Forward return over 60 minutes
- `target_future_return_18b`: Forward return over 90 minutes
- `target_class_up_60m`: Binary indicator ($\text{return} > +0.50\%$)
- `target_class_down_60m`: Binary indicator ($\text{return} < -0.50\%$)
- `target_class_3way_60m`: 3-class target: UP (+1), FLAT (0), DOWN (-1)
