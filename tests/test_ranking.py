"""Tests for cross-sectional opportunity ranking and Information Coefficient evaluation."""

from datetime import datetime, timezone
import pandas as pd
import pytest

from src.ranking.opportunity_ranker import OpportunityRanker, RankedOpportunity


def test_opportunity_ranker_scoring_and_selection() -> None:
    ranker = OpportunityRanker(risk_penalty_lambda=0.5, base_friction_bps=7.0, top_k=2, min_opportunity_score_bps=1.0)
    ts = datetime(2026, 1, 7, 15, 0, tzinfo=timezone.utc)

    candidates = [
        {"symbol": "NVDA", "p_up": 0.65, "expected_return_bps": 25.0, "realized_vol_pct": 0.002, "spread_bps": 1.0},
        {"symbol": "AMD", "p_up": 0.60, "expected_return_bps": 18.0, "realized_vol_pct": 0.002, "spread_bps": 1.2},
        {"symbol": "AAPL", "p_up": 0.54, "expected_return_bps": 8.0, "realized_vol_pct": 0.001, "spread_bps": 0.8},
        {"symbol": "JNJ", "p_up": 0.51, "expected_return_bps": 4.0, "realized_vol_pct": 0.0005, "spread_bps": 0.8},
    ]

    ranked = ranker.rank_universe_at_timestamp(ts, candidates)
    assert len(ranked) == 4
    assert ranked[0].symbol == "NVDA"
    assert ranked[0].rank == 1
    assert ranked[0].is_selected is True
    assert ranked[1].is_selected is True
    assert ranked[2].is_selected is False  # Top 2 only


def test_cross_sectional_ic_evaluation() -> None:
    ts_list = [datetime(2026, 1, 7, 14, i, tzinfo=timezone.utc) for i in range(10)]
    records = []
    for ts in ts_list:
        for i, sym in enumerate(["AAPL", "MSFT", "NVDA", "AMD", "AMZN"]):
            records.append({
                "timestamp": ts,
                "symbol": sym,
                "net_opportunity_score": float(5.0 * i),
                "target_future_return_6b": float(0.001 * i),
            })
    df = pd.DataFrame(records)

    eval_res = OpportunityRanker.evaluate_cross_sectional_ic(df)
    assert eval_res.mean_spearman_ic == pytest.approx(1.0, abs=1e-3)
    assert eval_res.long_short_spread_bps > 0.0
