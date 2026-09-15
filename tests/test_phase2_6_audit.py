"""Full integration test verifying the Phase 2.6 multi-horizon and ranking research suite."""

import numpy as np
import pandas as pd
import pytest

from src.data.loader import HistoricalDataLoader
from src.features.engine import FeatureEngine
from src.features.contracts import FeatureContractValidator
from src.evaluation.decay import SignalDecayAnalyzer
from src.ranking.opportunity_ranker import OpportunityRanker
from src.models.meta_labeling import MetaLabelingFilter
from src.models.trees import XGBoostModel
from src.strategies.ml_strategy import MLSignalStrategy
from src.evaluation.multiple_testing import MultipleTestingLedger, TrialRecord


def test_phase2_6_full_research_pipeline() -> None:
    # 1. Ingest Data for Multi-Asset Universe
    symbols = ["AAPL", "NVDA", "AMD", "SPY"]
    dfs = []
    for s in symbols:
        raw_df = HistoricalDataLoader.generate_synthetic_5m_data(symbol=s, num_days=5, seed=len(s))
        eng = FeatureEngine(include_targets=True)
        feat_df = eng.compute_all_features(raw_df)
        dfs.append(feat_df)

    universe_df = pd.concat(dfs, ignore_index=True)
    valid_features = FeatureContractValidator.get_feature_columns(universe_df)

    # 2. Multi-Horizon Target Verification
    assert "target_return_15m" in universe_df.columns
    assert "target_return_30m" in universe_df.columns
    assert "target_return_60m" in universe_df.columns

    # 3. Train Model on 15m Horizon
    nvda_df = universe_df[universe_df["symbol"] == "NVDA"].dropna(subset=valid_features + ["target_class_up_15m_10bps"]).reset_index(drop=True)
    split = len(nvda_df) // 2
    train_nvda = nvda_df.iloc[:split]
    test_nvda = nvda_df.iloc[split:]

    m15 = XGBoostModel(model_id="xgb_15m", n_estimators=20, max_depth=3)
    m15.fit(train_nvda[valid_features], train_nvda["target_class_up_15m_10bps"])

    # 4. Signal Decay Analysis
    strat = MLSignalStrategy(model=m15, min_confidence=0.52)
    signals = strat.generate_signals(test_nvda)
    decay_report = SignalDecayAnalyzer.compute_decay_curve(test_nvda, signals, model_id="xgb_15m")
    assert decay_report.model_id == "xgb_15m"
    assert len(decay_report.decay_curve) > 0

    # 5. Cross-Sectional Opportunity Ranking
    ranker = OpportunityRanker(risk_penalty_lambda=0.5, top_k=2)
    candidates = [
        {"symbol": s, "p_up": 0.60, "expected_return_bps": 20.0, "realized_vol_pct": 0.002}
        for s in symbols
    ]
    ranked = ranker.rank_universe_at_timestamp(test_nvda["timestamp"].iloc[0], candidates)
    assert len(ranked) == len(symbols)

    # 6. Meta-Labeling Filter
    meta_filter = MetaLabelingFilter(n_estimators=15, max_depth=2)
    probs_train = m15.predict_proba(train_nvda[valid_features])[:, 1]
    meta_filter.fit_meta_model(train_nvda, probs_train, train_nvda["target_return_15m"])

    # 7. Multiple-Testing Ledger
    ledger = MultipleTestingLedger()
    ledger.record_trial(
        TrialRecord(
            trial_id="T_15m_xgb",
            horizon_minutes=15,
            target_name="target_class_up_15m_10bps",
            model_type="XGBoost",
            threshold_value=0.52,
            features_count=len(valid_features),
            gross_return_pct=0.95,
            net_return_pct=0.35,
            sharpe_ratio=1.12,
            profit_factor=1.45,
            p_value=0.035,
        )
    )
    ledger.apply_corrections()
    assert len(ledger.trials) == 1
