"""
Unit tests for PositionRoundingEngine.
"""

import pytest
from src.execution.position_rounding import PositionRoundingEngine


def test_whole_share_rounding():
    engine = PositionRoundingEngine(allow_fractional=False)
    # Target $450, share price $120 -> 3 shares ($360 actual, $90 residual error)
    res = engine.round_position(target_dollars=450.0, share_price=120.0)
    assert res.rounded_shares == 3.0
    assert res.actual_notional_dollars == 360.0
    assert res.rounding_error_dollars == 90.0


def test_fractional_share_rounding():
    engine = PositionRoundingEngine(allow_fractional=True, fractional_precision=2)
    # Target $450, share price $120 -> 3.75 shares ($450 actual)
    res = engine.round_position(target_dollars=450.0, share_price=120.0)
    assert res.rounded_shares == 3.75
    assert res.actual_notional_dollars == 450.0
    assert round(res.rounding_error_dollars, 2) == 0.0


def test_share_price_higher_than_target():
    engine = PositionRoundingEngine(allow_fractional=False)
    # Target $200, share price $500 -> 0 shares
    res = engine.round_position(target_dollars=200.0, share_price=500.0)
    assert res.rounded_shares == 0.0
    assert res.actual_notional_dollars == 0.0
