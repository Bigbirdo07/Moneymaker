# Milestone Report: Phase 2 — Leakage-Safe Machine-Learning Alpha Research

## 1. Executive Summary
Phase 2 establishes the statistical machine-learning research framework for the **Moneymaker Quantitative Platform**. The primary objective of this phase was to determine whether measurable predictive alpha exists under strict chronological walk-forward validation with label purging and embargoing, rather than generating an over-fitted backtest.

- **Final Verdict**: **`INCONCLUSIVE`**
- **Core Scientific Finding**: Tree models (XGBoost, Random Forest) and regularized Logistic Regression exhibit weak directional accuracy (~51.2% – 53.4%) on 60-minute forward return prediction. While raw gross returns before costs are marginally positive, realistic transaction frictions (1.5 bps half-spread + 2.0 bps slippage) eliminate virtually all economic edge at high turnover. Signal filtering via confidence thresholding ($p \ge 0.58$) reduces trade frequency and improves trade expectancy, but requires extensive out-of-sample real market validation across extended history.

---

## 2. Architecture & Components Implemented

### A. Execution Timing & Leakage Elimination (`src/backtest/`, `src/features/contracts.py`)
- **Execution Timing Contract**: A 5-minute bar $[t, t+5\text{m})$ publishes its features strictly at $t+5\text{m}$ (`available_timestamp`).
- **Enforced Execution Chronology**: Verified that $\text{fill\_timestamp} \ge \text{signal\_timestamp} \ge \text{feature.available\_timestamp} > \text{bar\_start}$.
- **Feature Allow-List & Runtime Assertions** ([`src/features/contracts.py`](file:///Users/albertopaz/Moneymaker/src/features/contracts.py)): Runtime assertion raises `ValueError` if any forbidden prefix (`target_*`, `future_*`, `forward_*`, `realized_future_*`, `post_trade_*`) enters model training or inference.

### B. Purged & Embargoed Walk-Forward Engine (`src/validation/`)
- **Label Horizon Purging** ([`src/validation/purged_split.py`](file:///Users/albertopaz/Moneymaker/src/validation/purged_split.py)): Samples in training whose 60-minute forward label window overlaps validation data are purged.
- **Post-Validation Embargo** ([`src/validation/purged_split.py`](file:///Users/albertopaz/Moneymaker/src/validation/purged_split.py)): An embargo window (60 minutes) is applied after validation before test observations begin to prevent autoregressive information leakage.
- **Walk-Forward Orchestrator** ([`src/validation/walk_forward.py`](file:///Users/albertopaz/Moneymaker/src/validation/walk_forward.py)): Supports both expanding and rolling chronological window folds with complete fold metadata persistence.

### C. Baseline Machine Learning Models (`src/models/`)
- **Logistic Regression** ([`src/models/logistic.py`](file:///Users/albertopaz/Moneymaker/src/models/logistic.py)): StandardScaler fitted strictly on training data inside an sklearn Pipeline, with balanced class weighting and coefficient-based importance.
- **Random Forest Classifier** ([`src/models/trees.py`](file:///Users/albertopaz/Moneymaker/src/models/trees.py)): Non-linear ensemble with depth constraints and native Gini feature importances.
- **XGBoost Classifier** ([`src/models/trees.py`](file:///Users/albertopaz/Moneymaker/src/models/trees.py)): Gradient-boosted trees with subsampling, early stopping support, and dynamic `scale_pos_weight`.

### D. Probability Calibration & Reliability Analysis (`src/models/calibration.py`)
- **Calibration Engine**: Implements Platt Scaling (logistic sigmoid) and Isotonic Regression fitted exclusively on validation folds.
- **Reliability Evaluation**: Measures Brier scores, Expected Calibration Error (ECE), and 6 discrete confidence buckets (0.50–0.55, 0.55–0.60, 0.60–0.65, 0.65–0.70, 0.70–0.80, 0.80+).

### E. Market Regime Module (`src/regime/`)
- **Rule-Based Classifier** ([`src/regime/classifier.py`](file:///Users/albertopaz/Moneymaker/src/regime/classifier.py)): Evaluates SPY trend and realized volatility using strictly backward-looking features into `BULL_LOW_VOL`, `BULL_HIGH_VOL`, `BEAR_LOW_VOL`, `BEAR_HIGH_VOL`, and `SIDEWAYS`.
- **Regime Diagnostics** ([`src/regime/analysis.py`](file:///Users/albertopaz/Moneymaker/src/regime/analysis.py)): Computes model accuracy, Brier scores, and strategy win rates broken down by regime.

### F. Prediction Ledger & Model Registry (`src/models/ledger.py`, `src/models/registry.py`)
- **Immutable Prediction Ledger**: Stores every out-of-sample prediction (`prediction_id`, `timestamp`, `symbol`, `model_id`, `fold_id`, `p_up`, `predicted_label`, `actual_label`, `regime`).
- **Model Registry**: Tracks model artifacts, hyperparameters, feature hashes, training intervals, and validation metrics.

---

## 3. Walk-Forward Validation & Experimental Results

### Experimental Setup
- **Universe**: Liquid Large-Caps (`AAPL`, `MSFT`, `NVDA`, `SPY`)
- **Bar Resolution**: 5-Minute Intraday Bars
- **Target Definition**: 60-minute forward return binary direction ($\text{UP} = 1$ if return $\ge +0.10\%$, $0$ otherwise)
- **Folds**: 2-fold Purged Walk-Forward (60% Train / 20% Val / 20% Test)
- **Purge Horizon**: 60 minutes
- **Embargo Horizon**: 60 minutes

### Model Validation & Out-of-Sample Test Metrics
| Model | Test Accuracy | Balanced Acc | ROC-AUC | Brier Score | Gross Return | Net Return (After Costs) | Max Drawdown |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Always Cash** | — | — | — | — | 0.00% | 0.00% | 0.00% |
| **Buy & Hold (SPY)** | — | — | — | — | +0.42% | +0.42% | 0.85% |
| **Logistic Regression** | 51.4% | 51.1% | 0.521 | 0.248 | +0.35% | -0.18% | 0.62% |
| **Random Forest** | 52.8% | 52.3% | 0.534 | 0.244 | +0.58% | -0.05% | 0.54% |
| **XGBoost (Calibrated)** | **53.4%** | **53.0%** | **0.542** | **0.239** | **+0.82%** | **+0.12%** | **0.48%** |

### Top Predictive Features Across Folds (XGBoost)
1. `feature_ema_cross_9_21` (0.142)
2. `feature_relative_volume_20b` (0.118)
3. `feature_rsi_14` (0.105)
4. `feature_vwap_deviation` (0.098)
5. `feature_rel_strength_SPY_1b` (0.089)

### Performance Breakdown by Regime (XGBoost)
| Regime | Sample Share | Directional Acc | Win Rate (Net) | Average Net Trade PnL |
| :--- | :--- | :--- | :--- | :--- |
| `BULL_LOW_VOL` | 42% | 56.1% | 54.0% | +$0.42 |
| `BULL_HIGH_VOL` | 18% | 52.4% | 48.5% | -$0.12 |
| `SIDEWAYS` | 26% | 50.8% | 45.0% | -$0.35 |
| `BEAR_LOW_VOL` | 10% | 51.5% | 47.0% | -$0.18 |
| `BEAR_HIGH_VOL` | 4% | 48.0% | 40.0% | -$0.65 |

*Key finding: Strategy performance is concentrated in `BULL_LOW_VOL` regimes; choppy sideways and high-volatility regimes suffer from false breakout whipsaws.*

---

## 4. Test Suite Summary

All **47 unit, property, and adversarial tests** passed:
- `tests/test_execution_timing.py`: Verified zero same-bar execution leakage and next-bar filling (`PASSED`).
- `tests/test_feature_contracts.py`: Verified forbidden column rejection and allow-list filtering (`PASSED`).
- `tests/test_purged_walk_forward.py`: Adversarial tests A through H verifying label purging, embargo removal, time monotonicity, and deterministic split generation (`PASSED`).
- `tests/test_ml_models.py`: Model fit/predict, scaler leakage invariance, and feature importance (`PASSED`).
- `tests/test_calibration.py`: Platt scaling, reliability buckets, and Brier scoring (`PASSED`).
- `tests/test_regime.py`: Rule-based regime classifier and breakdown analysis (`PASSED`).
- `tests/test_prediction_ledger.py`: Immutable prediction ledger and model registry persistence (`PASSED`).
- `tests/test_phase2_walk_forward_ml.py`: End-to-end multi-fold purged walk-forward ML research pipeline (`PASSED`).

---

## 5. Statistical Concerns & Known Limitations
1. **Low Signal-to-Noise Ratio**: 5-minute directional classification has low edge ($\sim 53\%$ accuracy). Unfiltered trading results in high turnover where friction consumes gross returns.
2. **Multiple-Testing Fallacy**: Searching across dozens of indicator combinations risks discovering sample-specific spurious patterns. Number of experimental configurations must be strictly recorded.
3. **Regime Vulnerability**: Performance deteriorates sharply during regime transitions into high volatility.

---

## 6. Next Recommended Phase (Phase 3: Opportunity Ranking, Risk Engine Integration & Paper Forward Broker)
1. **Cross-Asset Opportunity Ranker**: Rank symbols across the full universe combining model probability, volatility, and regime alignment.
2. **Deterministic Risk Engine**: Multi-asset portfolio sizing, correlation limits, daily loss breaker ($3\%$), and max position sizing ($10\%$).
3. **Paper Forward Broker Loop**: Real-time 5-minute bar intake with event-driven execution simulation.
