"""Full integration test verifying the Phase 2.5 multi-fold statistical audit suite."""

import numpy as np
import pandas as pd
import pytest

from src.data.loader import HistoricalDataLoader
from src.features.engine import FeatureEngine
from src.features.contracts import FeatureContractValidator
from src.validation.walk_forward import WalkForwardEngine
from src.validation.cross_sectional import CrossSectionalValidator
from src.models.trees import XGBoostModel
from src.models.calibration import ProbabilityCalibrator
from src.strategies.ml_strategy import MLSignalStrategy
from src.backtest.engine import BacktestEngine
from src.backtest.costs import TransactionCostModel
from src.evaluation.metrics import MetricsCalculator
from src.evaluation.significance import SignificanceTester
from src.evaluation.stress_testing import StrategyStressTester


def test_full_phase_2_5_statistical_audit() -> None:
    # 1. Multi-symbol Dataset (Tech + Financials + Healthcare)
    symbols = ["AAPL", "MSFT", "JPM", "UNH"]
    sector_map = {"technology": ["AAPL", "MSFT"], "financials": ["JPM"], "healthcare": ["UNH"]}
    
    dfs = []
    for s in symbols:
        raw_s = HistoricalDataLoader.generate_synthetic_5m_data(symbol=s, num_days=12, seed=len(s))
        eng = FeatureEngine(include_targets=True)
        f_s = eng.compute_all_features(raw_s)
        dfs.append(f_s)

    universe_df = pd.concat(dfs, ignore_index=True)
    valid_features = FeatureContractValidator.get_feature_columns(universe_df)

    # 2. Multi-fold Walk-Forward (5 Folds)
    aapl_df = universe_df[universe_df["symbol"] == "AAPL"].sort_values("timestamp").reset_index(drop=True)
    wf_engine = WalkForwardEngine(n_splits=5, train_ratio=0.50, val_ratio=0.25, test_ratio=0.25)
    folds = wf_engine.generate_folds(aapl_df)
    assert len(folds) >= 3

    # 3. Model & Frozen Hypothesis Evaluation
    fold = folds[0]
    train_data = aapl_df.iloc[fold.train_indices].dropna(subset=valid_features + ["target_class_up_60m"])
    val_data = aapl_df.iloc[fold.val_indices].dropna(subset=valid_features + ["target_class_up_60m"])
    test_data = aapl_df.iloc[fold.test_indices].dropna(subset=valid_features + ["target_class_up_60m"])

    X_train, y_train = train_data[valid_features], train_data["target_class_up_60m"]
    X_val, y_val = val_data[valid_features], val_data["target_class_up_60m"]
    X_test, y_test = test_data[valid_features], test_data["target_class_up_60m"]

    model = XGBoostModel(model_id="audit_xgb", n_estimators=25, max_depth=3)
    model.fit(X_train, y_train, X_val=X_val, y_val=y_val)

    calibrator = ProbabilityCalibrator(method="sigmoid")
    calibrator.fit(model, X_val, y_val)

    # 4. Permutation Null Test
    null_res = SignificanceTester.run_permutation_null_test(
        model=model,
        X_test=X_test,
        y_test=y_test,
        num_permutations=20,
        seed=42,
    )
    assert "roc_auc" in null_res
    assert null_res["roc_auc"].empirical_p_value >= 0.0

    # 5. Backtest & Bootstrap Uncertainty
    strat = MLSignalStrategy(model=model, calibrator=calibrator, min_confidence=0.52)
    cost_mod = TransactionCostModel(half_spread_bps=1.5, base_slippage_bps=2.0)
    backtester = BacktestEngine(initial_capital=1000.0, max_position_pct=0.10, cost_model=cost_mod)
    bt_res = backtester.run(strat, test_data)

    calc = MetricsCalculator()
    summary = calc.compute_summary(bt_res)
    assert summary.initial_capital == 1000.0

    returns = bt_res.equity_curve["returns"].values
    boot_ci = SignificanceTester.compute_bootstrap_ci(returns, num_bootstraps=50, block_size=6)
    assert "annualized_return" in boot_ci

    # 6. Cost Sensitivity & Break-Even
    stress_results, break_even_bps = StrategyStressTester.run_cost_sensitivity_stress_test(
        strategy=strat,
        df=test_data,
        multipliers=[0.0, 1.0, 2.0],
    )
    assert len(stress_results) == 3
    assert break_even_bps >= 0.0
