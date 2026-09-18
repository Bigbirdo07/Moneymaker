"""
Property-based monotonicity tests for RiskPositionSizer.
"""

import pytest
from src.risk.portfolio_risk_state import PortfolioRiskState
from src.risk.risk_position_sizer import RiskPositionSizer, SizingDecision


def test_monotonicity_higher_volatility_never_increases_dollar_size():
    sizer = RiskPositionSizer()
    state = PortfolioRiskState.create(
        timestamp="2025-01-15T10:00:00Z",
        starting_day_equity=1000.0,
        current_equity=1000.0,
        cash=1000.0,
        peak_equity=1000.0,
        realized_pnl_today=0.0,
    )

    size_low_vol = sizer.size_position(
        portfolio_state=state,
        symbol="SYM",
        share_price=10.0,
        intraday_vol_bps=60.0,
        adv_dollars_30d=500_000_000.0,
    )

    size_high_vol = sizer.size_position(
        portfolio_state=state,
        symbol="SYM",
        share_price=10.0,
        intraday_vol_bps=250.0,
        adv_dollars_30d=500_000_000.0,
    )

    assert size_low_vol.final_allowed_dollars >= size_high_vol.final_allowed_dollars


def test_monotonicity_higher_equity_scales_monotonically():
    sizer = RiskPositionSizer()
    state_1k = PortfolioRiskState.create(
        timestamp="2025-01-15T10:00:00Z",
        starting_day_equity=1000.0,
        current_equity=1000.0,
        cash=1000.0,
        peak_equity=1000.0,
        realized_pnl_today=0.0,
    )
    state_5k = PortfolioRiskState.create(
        timestamp="2025-01-15T10:00:00Z",
        starting_day_equity=5000.0,
        current_equity=5000.0,
        cash=5000.0,
        peak_equity=5000.0,
        realized_pnl_today=0.0,
    )

    dec_1k = sizer.size_position(state_1k, "SYM", 20.0, 100.0, 500_000_000.0)
    dec_5k = sizer.size_position(state_5k, "SYM", 20.0, 100.0, 500_000_000.0)

    assert dec_5k.final_allowed_dollars >= dec_1k.final_allowed_dollars
    assert dec_5k.risk_dollars >= dec_1k.risk_dollars


def test_event_veto_strictly_forces_zero_size():
    sizer = RiskPositionSizer()
    state = PortfolioRiskState.create(
        timestamp="2025-01-15T10:00:00Z",
        starting_day_equity=1000.0,
        current_equity=1000.0,
        cash=1000.0,
        peak_equity=1000.0,
        realized_pnl_today=0.0,
    )

    # Event risk multiplier = 0.0 (VETO)
    dec = sizer.size_position(
        state, "NVDA", 120.0, 100.0, 500_000_000.0,
        event_risk_multiplier=0.0,
    )
    assert dec.decision == SizingDecision.NO_POSITION
    assert dec.target_shares == 0.0
    assert dec.final_allowed_dollars == 0.0
