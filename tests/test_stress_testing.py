"""Tests for strategy stress testing, cost sensitivity, execution delays, and ablation."""

import pandas as pd
import pytest

from src.data.loader import HistoricalDataLoader
from src.features.engine import FeatureEngine
from src.models.trees import RandomForestModel
from src.strategies.ml_strategy import MLSignalStrategy
from src.evaluation.stress_testing import StrategyStressTester


@pytest.fixture
def stress_dataset() -> tuple[pd.DataFrame, RandomForestModel, MLSignalStrategy]:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=3, seed=42)
    engine = FeatureEngine(include_targets=True)
    feats = engine.compute_all_features(df).dropna().reset_index(drop=True)
    
    X = feats[[c for c in feats.columns if c.startswith("feature_")]]
    y = feats["target_class_up_60m"]
    
    model = RandomForestModel(model_id="stress_rf", n_estimators=15, max_depth=3)
    model.fit(X, y)
    strat = MLSignalStrategy(model=model, min_confidence=0.51)
    return feats, model, strat


def test_cost_sensitivity_and_break_even(stress_dataset: tuple[pd.DataFrame, RandomForestModel, MLSignalStrategy]) -> None:
    feats, _, strat = stress_dataset
    results, break_even_bps = StrategyStressTester.run_cost_sensitivity_stress_test(
        strategy=strat,
        df=feats,
        multipliers=[0.0, 1.0, 2.0, 3.0],
    )
    assert len(results) == 4
    assert break_even_bps >= 0.0


def test_execution_delay_test(stress_dataset: tuple[pd.DataFrame, RandomForestModel, MLSignalStrategy]) -> None:
    feats, model, _ = stress_dataset
    delay_results = StrategyStressTester.run_execution_delay_test(
        model=model,
        df=feats,
        delays=[0, 1, 2],
    )
    assert len(delay_results) == 3
    assert delay_results[0].delay_minutes == 0
    assert delay_results[1].delay_minutes == 5


def test_feature_ablation(stress_dataset: tuple[pd.DataFrame, RandomForestModel, MLSignalStrategy]) -> None:
    feats, _, _ = stress_dataset
    split = len(feats) // 2
    train_df, test_df = feats.iloc[:split], feats.iloc[split:]

    families = {
        "momentum": ["feature_rsi_14", "feature_macd_line"],
        "volatility": ["feature_atr_14", "feature_realized_vol_20b"],
    }
    ablation_df = StrategyStressTester.run_feature_ablation(
        model_factory=lambda: RandomForestModel(model_id="ab_rf", n_estimators=10, max_depth=3),
        train_df=train_df,
        test_df=test_df,
        feature_families=families,
    )
    assert len(ablation_df) >= 3
    assert "ablated_family" in ablation_df.columns
