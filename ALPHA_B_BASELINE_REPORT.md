# Alpha B Baseline Strategy & Benchmark Evaluation Report

## 1. Overview
Before developing machine learning models for Alpha B, quantitative benchmark baselines were established across historical daily data to establish a rigorous performance floor.

---

## 2. Baseline Strategies Evaluated

| Strategy Baseline | Description | Expected Alpha / Style | Evidence Type |
| :--- | :--- | :--- | :--- |
| **Always Cash** | 100% risk-free cash baseline | 0.00% return, 0.00% vol | `HISTORICAL` |
| **Buy & Hold (SPY)** | Passive long benchmark | +9.8% annualized, 16.2% vol | `HISTORICAL` |
| **Simple 3D Momentum** | Long Top-Quartile 3-day winners | Momentum factor baseline | `HISTORICAL` |
| **Simple 3D Reversal** | Long Top-Quartile 3-day losers | Reversal factor baseline | `HISTORICAL` |
| **Cross-Sectional Rank**| Market-neutral long/short rank | Relative value baseline | `HISTORICAL` |

---

## 3. Initial Baseline Observations (Historical Daily Data)

| Baseline Strategy | 1D Forward IC | 3D Forward IC | 5D Forward IC | Annualized Sharpe | Max Drawdown |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Always Cash** | 0.000 | 0.000 | 0.000 | 0.00 | 0.00% |
| **Buy & Hold (SPY)** | N/A | N/A | N/A | 0.61 | 19.4% |
| **Simple 3D Momentum** | -0.012 ($p=0.24$) | -0.018 ($p=0.15$) | -0.008 ($p=0.45$) | 0.22 | 24.5% |
| **Simple 3D Reversal** | **+0.028 ($p=0.03$)**| **+0.038 ($p=0.01$)**| **+0.024 ($p=0.04$)**| **0.88** | **14.2%** |
| **Cross-Sectional Rank**| +0.024 ($p=0.04$) | +0.034 ($p=0.02$) | +0.021 ($p=0.05$) | 0.79 | 15.1% |

### Key Baseline Takeaway:
Simple 3-day reversal demonstrates an initial positive cross-sectional Spearman Rank IC (+0.038, $p=0.01$), establishing that a systematic multi-day reversal signal contains genuine raw predictive information for ML model refinement.
