"""Tests for configuration loading and Pydantic schema validation."""

from pathlib import Path
import pytest
from src.core.config import load_app_config, AppConfig


def test_load_app_config() -> None:
    config = load_app_config(config_dir="configs")
    assert isinstance(config, AppConfig)
    
    # Universe assertions
    assert len(config.universe.symbols) >= 15
    assert "SPY" in config.universe.symbols
    assert "AAPL" in config.universe.symbols
    assert config.universe.benchmarks["broad_market"] == "SPY"

    # Trading assertions
    assert config.trading.execution.initial_cash == 1000.0
    assert config.trading.execution.allow_shorting is False
    assert config.trading.execution.allow_leverage is False
    assert config.trading.live_execution_enabled is False

    # Risk assertions
    assert config.risk.portfolio.max_position_pct == 0.10
    assert config.risk.portfolio.max_daily_loss_pct == 0.03
    assert config.risk.portfolio.max_portfolio_drawdown_pct == 0.15
    assert config.risk.constraints.leverage_allowed is False
