"""
Unit tests for fail-closed behavior on missing or corrupted sizing data.
"""

import pytest
from src.risk.portfolio_risk_state import PortfolioRiskState
from src.risk.risk_position_sizer import RiskPositionSizer, SizingDecision


def test_missing_or_corrupted_inputs_fail_closed():
    sizer = RiskPositionSizer()
    state = PortfolioRiskState.create(
        timestamp="2025-01-15T10:00:00Z",
        starting_day_equity=1000.0,
        current_equity=1000.0,
        cash=1000.0,
        peak_equity=1000.0,
        realized_pnl_today=0.0,
    )

    # 1. Zero share price -> NO_POSITION
    d1 = sizer.size_position(state, "SYM", share_price=0.0, intraday_vol_bps=100.0, adv_dollars_30d=10_000_000.0)
    assert d1.decision == SizingDecision.NO_POSITION
    assert d1.target_shares == 0.0

    # 2. Negative volatility -> NO_POSITION
    d2 = sizer.size_position(state, "SYM", share_price=50.0, intraday_vol_bps=-10.0, adv_dollars_30d=10_000_000.0)
    assert d2.decision == SizingDecision.NO_POSITION
    assert d2.target_shares == 0.0

    # 3. Missing ADV (0.0) -> NO_POSITION
    d3 = sizer.size_position(state, "SYM", share_price=50.0, intraday_vol_bps=100.0, adv_dollars_30d=0.0)
    assert d3.decision == SizingDecision.NO_POSITION
    assert d3.target_shares == 0.0
