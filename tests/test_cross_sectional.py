"""Tests for cross-sectional generalization, leave-sector-out, and concentration analysis."""

import pandas as pd
import pytest

from src.data.loader import HistoricalDataLoader
from src.features.engine import FeatureEngine
from src.features.contracts import FeatureContractValidator
from src.models.trees import RandomForestModel
from src.validation.cross_sectional import CrossSectionalValidator
from src.backtest.engine import CompletedTrade
from datetime import datetime, timezone


def test_leave_sector_out_validation() -> None:
    # Build a small multi-sector universe
    aapl = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=3, seed=1)
    msft = HistoricalDataLoader.generate_synthetic_5m_data(symbol="MSFT", num_days=3, seed=2)
    jpm = HistoricalDataLoader.generate_synthetic_5m_data(symbol="JPM", num_days=3, seed=3)
    bac = HistoricalDataLoader.generate_synthetic_5m_data(symbol="BAC", num_days=3, seed=4)

    engine = FeatureEngine(include_targets=True)
    f_aapl = engine.compute_all_features(aapl)
    f_msft = engine.compute_all_features(msft)
    f_jpm = engine.compute_all_features(jpm)
    f_bac = engine.compute_all_features(bac)

    full_df = pd.concat([f_aapl, f_msft, f_jpm, f_bac], ignore_index=True)
    feature_cols = FeatureContractValidator.get_feature_columns(full_df)

    sector_map = {
        "technology": ["AAPL", "MSFT"],
        "financials": ["JPM", "BAC"],
    }

    results = CrossSectionalValidator.evaluate_leave_sector_out(
        model_factory=lambda: RandomForestModel(model_id="sec_rf", n_estimators=10, max_depth=3),
        universe_df=full_df,
        sector_symbol_map=sector_map,
        feature_cols=feature_cols,
    )

    assert len(results) == 2
    for res in results:
        assert res.sample_count > 0
        assert 0.0 <= res.accuracy <= 1.0


def test_pnl_concentration_analysis() -> None:
    trades = [
        CompletedTrade(
            trade_id=f"T_{i}",
            symbol="NVDA" if i < 8 else "AAPL",
            entry_timestamp=datetime(2026, 1, 7, 14, 0, tzinfo=timezone.utc),
            exit_timestamp=datetime(2026, 1, 7, 15, 0, tzinfo=timezone.utc),
            entry_price=100.0,
            exit_price=102.0 if i < 8 else 100.2,
            shares=10,
            gross_pnl=20.0 if i < 8 else 2.0,
            net_pnl=19.5 if i < 8 else 1.5,
            return_pct=0.0195,
            spread_paid=0.3,
            slippage_paid=0.2,
            commission_paid=0.0,
            holding_bars=12,
            exit_reason="TP",
            strategy="xgb",
        )
        for i in range(10)
    ]

    report = CrossSectionalValidator.analyze_pnl_concentration(trades, symbol_to_sector_map={"NVDA": "technology", "AAPL": "technology"})
    assert report.top_1_symbol_pnl_pct > 80.0
    assert report.is_concentrated is True
