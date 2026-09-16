# Moneymaker HPC Multiple Testing & Snooping Control Ledger

## 1. Multiple Testing Invariant

Greater computational scale on HPC clusters dramatically increases the risk of data snooping, p-hacking, and false discoveries.

To safeguard the scientific integrity of the platform:
1. **Every research hypothesis family executed on Unity must be recorded in this ledger prior to evaluation.**
2. **Deflated Sharpe Ratios (Bailey & López de Prado, 2014)** and False Discovery Rate (FDR / Benjamini-Hochberg) adjustments are computed automatically for all parameter search spaces.
3. No strategy parameter is ever selected based on in-sample peak performance.

---

## 2. Research Family Ledger

| Family ID | Strategy Target | Hypothesis / Search Space | Trials Count | Deflated Sharpe Adjusted Threshold | Outcome |
|---|---|---|---|---|---|
| `FAM_001` | `ALPHA_A` | Intraday relative momentum lookback window (5m vs 15m vs 30m) | 12 | 1.85 | **APPROVED (15m canonical)** |
| `FAM_002` | `ALPHA_A` | Dynamic spread slippage model calibration | 8 | 1.62 | **APPROVED (1.5x canonical)** |
| `FAM_003` | `ALPHA_B` | Mean-reversion holding period sweep (1d to 5d) | 10 | 1.74 | **APPROVED (3d canonical)** |
| `FAM_004` | `ALPHA_B` | Entry z-score threshold sweep (-1.5 to -3.0) | 15 | 1.92 | **APPROVED (-2.0 canonical)** |
| `FAM_005` | `PORTFOLIO` | Risk parity vs. Inverse Volatility dynamic weighting | 24 | 2.05 | **FORWARD_SHADOW_ONLY (Not live)** |
| `FAM_006` | `MMRM_01` | QLoRA rank (r=8, 16, 32, 64) and alpha scaling | 16 | N/A (LLM Benchmark) | **CANDIDATE (r=16, α=32)** |
