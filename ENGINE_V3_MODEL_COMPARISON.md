# Engine V3 Model Architecture & Comparison Report

## 1. Candidate Architectures Evaluated
- **Ridge Baseline**: Linear cross-sectional regressor.
- **HistGradientBoosting Multi-Horizon (V3 Candidate)**: Non-linear tree ensemble with isotonic calibration.
- **Two-Stage Market Gate + Ranker**: Combines Stage-1 macro filter with Stage-2 leader selection.