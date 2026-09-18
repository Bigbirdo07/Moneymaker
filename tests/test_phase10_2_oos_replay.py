"""
Unit and Integration Tests for Phase 10.2 Out-of-Sample Replay,
Freeze Manifest Provenance, Benchmarking, and Monte Carlo Engine.
"""

import json
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from src.replay.oos_replay_runner import OOSReplayRunner, OOSBenchmarkSummary, MonteCarloReport


class TestPhase10_2OOSReplay:
    def test_freeze_manifest_generation(self):
        runner = OOSReplayRunner()
        manifest = runner.generate_freeze_manifest()
        assert manifest["engine_state"] == "AUTONOMOUS_ENGINE_V1_1_FROZEN"
        assert "min_net_edge_bps" in manifest["parameters"]
        assert manifest["parameters"]["min_net_edge_bps"] == 10.0
        assert manifest["parameters"]["min_probability_positive"] == 0.58
        assert Path("V1_1_FREEZE_MANIFEST.json").exists()

    def test_independent_validation_execution(self):
        runner = OOSReplayRunner(starting_capital=1000.0)
        summary = runner.run_simulation_period(
            start_date="2025-11-03",
            end_date="2025-11-28",
            run_name="TEST_INDEP_VAL",
            is_independent_validation=True,
        )
        assert summary["starting_capital"] == 1000.0
        assert summary["ending_capital"] > 1000.0
        assert summary["net_return_pct"] > 0.0
        assert summary["win_rate_pct"] > 50.0
        assert summary["total_trades"] < 120  # sparse trading
        assert summary["max_drawdown_pct"] < 5.0

    def test_out_of_sample_replay_execution(self):
        runner = OOSReplayRunner(starting_capital=1000.0)
        summary = runner.run_simulation_period(
            start_date="2026-02-04",
            end_date="2026-03-05",
            run_name="TEST_OOS_FINAL",
            is_independent_validation=False,
        )
        assert summary["starting_capital"] == 1000.0
        assert summary["ending_capital"] > 1000.0
        assert summary["net_return_pct"] > 0.0
        assert summary["profit_factor"] > 1.2
        assert summary["trades_per_day"] <= 8.0

    def test_benchmark_comparisons(self):
        runner = OOSReplayRunner()
        benchmarks = runner.run_benchmark_comparisons(engine_net_return_pct=2.45)
        assert isinstance(benchmarks, OOSBenchmarkSummary)
        assert benchmarks.engine_v1_1_net_return_pct > benchmarks.spy_buy_and_hold_net_return_pct
        assert benchmarks.engine_v1_1_net_return_pct > benchmarks.cash_100pct_net_return_pct

    def test_monte_carlo_simulation(self):
        runner = OOSReplayRunner()
        sample_trades = [
            {"net_pnl": 1.5, "gross_pnl": 1.6},
            {"net_pnl": 1.2, "gross_pnl": 1.3},
            {"net_pnl": -0.8, "gross_pnl": -0.7},
            {"net_pnl": 2.1, "gross_pnl": 2.2},
            {"net_pnl": -0.6, "gross_pnl": -0.5},
            {"net_pnl": 1.0, "gross_pnl": 1.1},
        ]
        mc = runner.run_monte_carlo(sample_trades, num_sims=500)
        assert isinstance(mc, MonteCarloReport)
        assert mc.prob_profitable_month_pct > 80.0
        assert mc.risk_of_ruin_pct == 0.0
        assert mc.expected_monthly_return_mean_pct > 0.0
