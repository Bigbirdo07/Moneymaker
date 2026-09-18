"""
Unit tests for RiskPositionSizer.
"""

import pytest
from src.risk.portfolio_risk_state import PortfolioRiskState
from src.risk.risk_position_sizer import RiskPositionSizer, SizingDecision


def test_standard_position_sizing_approved():
    sizer = RiskPositionSizer()
    state = PortfolioRiskState.create(
        timestamp="2025-01-15T10:00:00Z",
        starting_day_equity=1000.0,
        current_equity=1000.0,
        cash=1000.0,
        peak_equity=1000.0,
        realized_pnl_today=0.0,
    )

    decision = sizer.size_position(
        portfolio_state=state,
        symbol="AMD",
        share_price=120.0,
        intraday_vol_bps=120.0,
        adv_dollars_30d=500_000_000.0,
        minute_dollar_volume=2_000_000.0,
        predicted_net_edge_bps=30.0,
        model_confidence=0.65,
    )

    assert decision.is_approved
    assert decision.decision in (SizingDecision.SIZE_APPROVED, SizingDecision.SIZE_REDUCED)
    assert decision.target_shares > 0
    assert decision.risk_dollars <= 12.0  # Bounded risk
    assert decision.final_allowed_dollars <= 750.0  # Respects 75% max tier exposure


def test_max_open_positions_blocks_new_trade():
    sizer = RiskPositionSizer()
    state = PortfolioRiskState.create(
        timestamp="2025-01-15T10:00:00Z",
        starting_day_equity=1000.0,
        current_equity=1000.0,
        cash=500.0,
        peak_equity=1000.0,
        realized_pnl_today=0.0,
    )
    # Inject existing position in tier paper ($1,000 max 1 position)
    from src.risk.portfolio_risk_state import PositionRecord
    state.open_positions["NVDA"] = PositionRecord(
        symbol="NVDA",
        shares=4.0,
        entry_price=120.0,
        current_price=120.0,
        entry_timestamp="2025-01-15T09:45:00Z",
        effective_stop_price=118.0,
        peak_price=120.0,
    )

    decision = sizer.size_position(
        portfolio_state=state,
        symbol="AMD",
        share_price=120.0,
        intraday_vol_bps=120.0,
        adv_dollars_30d=500_000_000.0,
    )

    assert not decision.is_approved
    assert decision.decision == SizingDecision.NO_POSITION
    assert any("MAX_OPEN_POSITIONS_REACHED" in r for r in decision.reason_codes)
