"""Tests for transaction cost model and backtest execution realism."""

import pytest
from src.core.types import OrderSide
from src.backtest.costs import TransactionCostModel, CostBreakdown


def test_transaction_cost_buy_and_sell() -> None:
    model = TransactionCostModel(
        half_spread_bps=2.0,   # 0.02%
        base_slippage_bps=3.0, # 0.03%
        commission_per_trade=1.0,
    )
    
    # 1. Test BUY fill
    price = 100.0
    shares = 10
    buy_fill = model.calculate_fill(side=OrderSide.BUY, price=price, shares=shares)
    
    # Expected friction: (2.0 + 3.0) bps = 5.0 bps = 0.05 per share
    assert buy_fill.net_price == pytest.approx(100.05, abs=1e-4)
    assert buy_fill.spread_cost == pytest.approx(0.20, abs=1e-4)
    assert buy_fill.slippage_cost == pytest.approx(0.30, abs=1e-4)
    assert buy_fill.commission == pytest.approx(1.0, abs=1e-4)
    assert buy_fill.total_friction == pytest.approx(1.50, abs=1e-4)

    # 2. Test SELL fill
    sell_fill = model.calculate_fill(side=OrderSide.SELL, price=price, shares=shares)
    assert sell_fill.net_price == pytest.approx(99.95, abs=1e-4)
    assert sell_fill.total_friction == pytest.approx(1.50, abs=1e-4)


def test_zero_shares_returns_zero_friction() -> None:
    model = TransactionCostModel()
    fill = model.calculate_fill(side=OrderSide.BUY, price=100.0, shares=0)
    assert fill.net_price == 100.0
    assert fill.total_friction == 0.0
