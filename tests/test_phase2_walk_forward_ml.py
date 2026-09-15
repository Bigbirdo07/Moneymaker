"""End-to-end integration test of Phase 2 ML research and purged walk-forward evaluation."""

import numpy as np
import pandas as pd
import pytest

from src.data.loader import HistoricalDataLoader
from src.features.engine import FeatureEngine
from src.features.contracts import FeatureContractValidator
from src.validation.walk_forward import WalkForwardEngine
from src.models.logistic import LogisticRegressionModel
from src.models.trees import RandomForestModel, XGBoostModel
from src.models.calibration import ProbabilityCalibrator
from src.models.metrics import compute_classification_metrics
from src.models.ledger import PredictionLedger, PredictionRecord
from src.regime.classifier import MarketRegimeClassifier
from src.strategies.ml_strategy import MLSignalStrategy
from src.backtest.engine import BacktestEngine
from src.backtest.costs import TransactionCostModel
from src.evaluation.metrics import MetricsCalculator


def test_phase2_walk_forward_ml_pipeline() -> None:
    # 1. Generate Dataset
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=15, seed=42)
    spy_df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="SPY", num_days=15, seed=99)

    engine = FeatureEngine(include_targets=True)
    features_df = engine.compute_all_features(df, benchmark_df=spy_df, benchmark_symbol="SPY")
    
    # Classify market regimes
    regime_clf = MarketRegimeClassifier()
    features_df["regime"] = regime_clf.classify_dataframe(features_df)

    # 2. Extract Validated Features & Clean Target
    valid_features = FeatureContractValidator.get_feature_columns(features_df)
    assert len(valid_features) >= 15

    # 3. Purged Walk-Forward Splitter
    wf_engine = WalkForwardEngine(n_splits=2, train_ratio=0.60, val_ratio=0.20, test_ratio=0.20)
    folds = wf_engine.generate_folds(features_df)
    assert len(folds) >= 1

    ledger = PredictionLedger()
    cost_model = TransactionCostModel(half_spread_bps=1.5, base_slippage_bps=2.0)
    backtester = BacktestEngine(initial_capital=1000.0, max_position_pct=0.10, cost_model=cost_model)
    calc = MetricsCalculator()

    for fold in folds:
        train_df = features_df.iloc[fold.train_indices].dropna(subset=valid_features + ["target_class_up_60m"])
        val_df = features_df.iloc[fold.val_indices].dropna(subset=valid_features + ["target_class_up_60m"])
        test_df = features_df.iloc[fold.test_indices].dropna(subset=valid_features + ["target_class_up_60m"])

        X_train, y_train = train_df[valid_features], train_df["target_class_up_60m"]
        X_val, y_val = val_df[valid_features], val_df["target_class_up_60m"]
        X_test, y_test = test_df[valid_features], test_df["target_class_up_60m"]

        # Models: Logistic, RF, XGB
        models = [
            LogisticRegressionModel(model_id=f"log_f{fold.fold_id}"),
            RandomForestModel(model_id=f"rf_f{fold.fold_id}", n_estimators=30, max_depth=3),
            XGBoostModel(model_id=f"xgb_f{fold.fold_id}", n_estimators=30, max_depth=3),
        ]

        for model in models:
            # Fit strictly on train
            model.fit(X_train, y_train, X_val=X_val, y_val=y_val)

            # Calibrate on validation
            calibrator = ProbabilityCalibrator(method="sigmoid")
            calibrator.fit(model, X_val, y_val)

            # Predict on unseen test
            test_probs = calibrator.predict_proba(model, X_test)
            test_preds = (test_probs[:, 1] >= 0.50).astype(int)

            metrics = compute_classification_metrics(y_test, test_preds, test_probs)
            assert 0.0 <= metrics.accuracy <= 1.0
            assert 0.0 <= metrics.brier_score <= 1.0

            # Record out-of-sample predictions
            for idx, (_, row) in enumerate(test_df.iterrows()):
                ledger.record_prediction(
                    PredictionRecord(
                        prediction_id=f"{model.model_id}_s{idx}",
                        timestamp=row["timestamp"],
                        symbol="AAPL",
                        model_id=model.model_id,
                        fold_id=fold.fold_id,
                        features_version="v1.0",
                        p_up=float(test_probs[idx, 1]),
                        p_down=float(test_probs[idx, 0]),
                        predicted_label=int(test_preds[idx]),
                        actual_label=int(y_test.iloc[idx]),
                        regime=str(row["regime"]),
                    )
                )

            # Run Backtest with calibrated strategy on test set
            strat = MLSignalStrategy(model=model, calibrator=calibrator, min_confidence=0.52)
            bt_res = backtester.run(strat, test_df)
            perf = calc.compute_summary(bt_res)
            assert perf.initial_capital == 1000.0

    ledger_df = ledger.to_dataframe()
    assert len(ledger_df) > 0
    assert "p_up" in ledger_df.columns
    assert "regime" in ledger_df.columns
