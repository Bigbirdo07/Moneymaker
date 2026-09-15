"""Tests for prediction ledger and model registry."""

from datetime import datetime, timezone
import pytest

from src.models.ledger import PredictionLedger, PredictionRecord
from src.models.registry import ModelRegistry
from src.models.base import ModelMetadata


def test_prediction_ledger_recording() -> None:
    ledger = PredictionLedger()
    rec = PredictionRecord(
        prediction_id="pred_001",
        timestamp=datetime(2026, 1, 7, 15, 0, tzinfo=timezone.utc),
        symbol="AAPL",
        model_id="xgb_v1",
        fold_id=1,
        features_version="v1.0",
        p_up=0.68,
        p_down=0.32,
        predicted_label=1,
        actual_label=1,
        expected_return=0.006,
        regime="BULL_LOW_VOL",
    )
    ledger.record_prediction(rec)
    df = ledger.to_dataframe()
    assert len(df) == 1
    assert df.iloc[0]["prediction_id"] == "pred_001"
    assert df.iloc[0]["p_up"] == 0.68


def test_model_registry() -> None:
    registry = ModelRegistry()
    meta = ModelMetadata(
        model_id="rf_v1",
        model_version="v1.0",
        model_type="RandomForest",
        feature_names=["feature_rsi_14"],
        target_name="target_class_up_60m",
        training_start="2026-01-05",
        training_end="2026-01-08",
        hyperparameters={"max_depth": 4},
        metrics={"roc_auc": 0.58},
    )
    registry.register_model(meta)
    retrieved = registry.get_metadata("rf_v1")
    assert retrieved is not None
    assert retrieved.model_type == "RandomForest"
