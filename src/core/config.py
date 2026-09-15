"""Configuration management and typed schema validation using Pydantic."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field


class UniverseSectorConfig(BaseModel):
    etf: str
    symbols: List[str]


class UniverseFiltersConfig(BaseModel):
    min_average_daily_volume: int = 1000000
    min_share_price: float = 10.0
    require_us_regular_hours: bool = True


class UniverseConfig(BaseModel):
    name: str = "us_liquid_largecap_v1"
    description: str = ""
    benchmarks: Dict[str, str] = Field(default_factory=lambda: {"broad_market": "SPY", "tech_growth": "QQQ"})
    sectors: Dict[str, UniverseSectorConfig] = Field(default_factory=dict)
    symbols: List[str] = Field(default_factory=list)
    filters: UniverseFiltersConfig = Field(default_factory=UniverseFiltersConfig)


class MarketConfig(BaseModel):
    exchange: str = "NYSE_NASDAQ"
    timezone: str = "UTC"
    market_timezone: str = "America/New_York"
    regular_hours_only: bool = True
    open_time: str = "09:30:00"
    close_time: str = "16:00:00"
    force_close_minutes_before_end: int = 10


class ExecutionConfig(BaseModel):
    initial_cash: float = 1000.0
    order_type: str = "MARKET"
    allow_shorting: bool = False
    allow_leverage: bool = False
    allow_options: bool = False
    slippage_bps: float = 2.0
    half_spread_bps: float = 1.5
    commission_per_trade: float = 0.0


class TradingThresholdsConfig(BaseModel):
    min_model_confidence: float = 0.55
    min_expected_return_bps: float = 15.0
    min_expected_return_after_costs_bps: float = 5.0
    min_risk_reward_ratio: float = 1.5


class TradingConfig(BaseModel):
    timeframe: str = "5m"
    default_mode: str = "BACKTEST"
    live_execution_enabled: bool = False
    market: MarketConfig = Field(default_factory=MarketConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    thresholds: TradingThresholdsConfig = Field(default_factory=TradingThresholdsConfig)


class PortfolioRiskConfig(BaseModel):
    initial_capital: float = 1000.0
    max_position_pct: float = 0.10
    max_risk_per_trade_pct: float = 0.01
    max_daily_loss_pct: float = 0.03
    max_portfolio_drawdown_pct: float = 0.15
    max_sector_exposure_pct: float = 0.25
    max_concurrent_positions: int = 5


class RiskConstraintsConfig(BaseModel):
    leverage_allowed: bool = False
    shorting_allowed: bool = False
    options_allowed: bool = False
    overnight_holding_allowed: bool = False


class RiskVetoRulesConfig(BaseModel):
    check_buying_power: bool = True
    check_daily_drawdown_limit: bool = True
    check_max_concurrent_positions: bool = True
    check_sector_concentration: bool = True
    check_correlation_concentration: bool = True


class RiskConfig(BaseModel):
    portfolio: PortfolioRiskConfig = Field(default_factory=PortfolioRiskConfig)
    constraints: RiskConstraintsConfig = Field(default_factory=RiskConstraintsConfig)
    veto_rules: RiskVetoRulesConfig = Field(default_factory=RiskVetoRulesConfig)


class AppConfig(BaseModel):
    """Unified application configuration."""
    universe: UniverseConfig
    trading: TradingConfig
    risk: RiskConfig
    models_raw: Dict[str, Any] = Field(default_factory=dict)


def load_yaml(file_path: Path | str) -> Dict[str, Any]:
    """Safely loads a YAML file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_app_config(config_dir: Path | str = "configs") -> AppConfig:
    """Loads all system configuration files from the config directory."""
    base_dir = Path(config_dir)
    
    universe_data = load_yaml(base_dir / "universe.yaml").get("universe", {})
    trading_data = load_yaml(base_dir / "trading.yaml").get("trading", {})
    risk_data = load_yaml(base_dir / "risk.yaml").get("risk", {})
    models_data = load_yaml(base_dir / "models.yaml")

    return AppConfig(
        universe=UniverseConfig(**universe_data),
        trading=TradingConfig(**trading_data),
        risk=RiskConfig(**risk_data),
        models_raw=models_data,
    )
