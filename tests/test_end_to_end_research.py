"""End-to-end integration test of the historical quantitative research engine."""

import pytest
from src.data.loader import HistoricalDataLoader
from src.data.validation import DataValidator
from src.features.engine import FeatureEngine
from src.strategies.baselines import AlwaysCashStrategy, BuyAndHoldStrategy
from src.strategies.momentum import BaselineMomentumStrategy
from src.strategies.mean_reversion import BaselineMeanReversionStrategy
from src.backtest.engine import BacktestEngine
from src.backtest.costs import TransactionCostModel
from src.evaluation.metrics import MetricsCalculator
from src.evaluation.reports import ResearchReportGenerator


def test_end_to_end_historical_research_flow() -> None:
    # 1. Ingest Market Data for Asset and Benchmark
    aapl_df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=5, seed=42)
    spy_df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="SPY", num_days=5, seed=99)

    # 2. Data Validation
    validator = DataValidator()
    aapl_report = validator.validate(aapl_df, symbol="AAPL")
    spy_report = validator.validate(spy_df, symbol="SPY")
    assert aapl_report.is_valid is True
    assert spy_report.is_valid is True

    # 3. Feature Pipeline with Market Context
    engine = FeatureEngine(include_targets=True)
    features_df = engine.compute_all_features(aapl_df, benchmark_df=spy_df, benchmark_symbol="SPY")

    assert "feature_rsi_14" in features_df.columns
    assert "feature_relative_volume_20b" in features_df.columns
    assert "feature_rel_strength_SPY_1b" in features_df.columns
    assert "target_future_return_12b" in features_df.columns

    # 4. Run Backtesting for Baseline Strategies
    cost_model = TransactionCostModel(half_spread_bps=1.5, base_slippage_bps=2.0)
    backtester = BacktestEngine(initial_capital=1000.0, max_position_pct=0.10, cost_model=cost_model)

    # Benchmark: Buy and Hold
    res_bnh = backtester.run(BuyAndHoldStrategy(), features_df)
    # Baseline Strategy: Momentum
    res_mom = backtester.run(BaselineMomentumStrategy(), features_df)
    # Baseline Strategy: Mean Reversion
    res_mr = backtester.run(BaselineMeanReversionStrategy(), features_df)

    # 5. Performance Metrics
    calc = MetricsCalculator()
    summary_bnh = calc.compute_summary(res_bnh)
    summary_mom = calc.compute_summary(res_mom, benchmark_equity_curve=res_bnh.equity_curve)
    summary_mr = calc.compute_summary(res_mr, benchmark_equity_curve=res_bnh.equity_curve)

    assert summary_bnh.initial_capital == 1000.0
    assert summary_mom.initial_capital == 1000.0
    assert summary_mr.initial_capital == 1000.0

    # 6. Generate Research Report
    report_md = ResearchReportGenerator.generate_strategy_report(
        summary=summary_mom,
        hypothesis="Intraday momentum breakouts on 5-minute bars produce positive alpha after spreads and slippage.",
        universe="US_LIQUID_LARGECAP_V1",
        start_date="2026-01-05",
        end_date="2026-01-09",
        benchmark_summary=summary_bnh,
        verdict="INCONCLUSIVE",
    )

    assert "# Quantitative Research Report: baseline_momentum" in report_md
    assert "Cost & Friction Drag Breakdown" in report_md
