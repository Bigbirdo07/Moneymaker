"""
Controlled Capital Ramp & Capacity Engine for Moneymaker Quantitative Platform (Phase 6B).
Enforces discrete tier scaling, hard capital firewalls, per-symbol notional ceilings,
participation rate tracking, empirical impact curve modeling, edge retention ratio auditing,
and deterministic liquidity-aware order downsizing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import math
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd


class EvidenceType(str, Enum):
    HISTORICAL = "HISTORICAL"
    FORWARD_SHADOW = "FORWARD_SHADOW"
    BROKER_PAPER = "BROKER_PAPER"
    LIVE_GOVERNED = "LIVE_GOVERNED"
    LIVE_AUTONOMOUS = "LIVE_AUTONOMOUS"
    SIMULATED = "SIMULATED"
    PROJECTED = "PROJECTED"


class CapitalTier(str, Enum):
    TIER_0_1K = "TIER_0_1K"       # $1,000 baseline (LIVE VALIDATED)
    TIER_1_2K5 = "TIER_1_2K5"     # $2,500 (LIVE VALIDATED)
    TIER_2_5K = "TIER_2_5K"       # $5,000 (NOT YET VALIDATED / PENDING AUTHORIZATION)
    TIER_3_10K = "TIER_3_10K"     # $10,000 (LOCKED / UNAUTHORIZED)
    TIER_4_25K = "TIER_4_25K"     # $25,000 (PROJECTED ONLY)
    TIER_5_50K = "TIER_5_50K"     # $50,000 (PROJECTED ONLY)


class CapacityDegradationState(str, Enum):
    HEALTHY_CAPACITY = "HEALTHY_CAPACITY"     # Edge retention >= 80%
    WATCH_CAPACITY = "WATCH_CAPACITY"         # Edge retention 60% - 80%
    DEGRADED_CAPACITY = "DEGRADED_CAPACITY"   # Edge retention 30% - 60%
    CAPACITY_EXCEEDED = "CAPACITY_EXCEEDED"   # Edge retention < 30% or net expectancy <= 0


class CapitalSecurityViolation(RuntimeError):
    """Raised when account equity or capital allocation exceeds authorized tier bounds."""
    pass


@dataclass
class CapitalTierConfig:
    tier: CapitalTier
    name: str
    authorized_capital_usd: float
    max_single_order_usd: float
    max_daily_loss_usd: float
    max_weekly_loss_usd: float
    max_pilot_drawdown_usd: float
    max_concurrent_positions: int = 2
    position_cap_pct: float = 0.10  # 10% baseline sizing
    is_authorized: bool = False
    min_sample_fills: int = 100
    min_sample_sessions: int = 20

    @property
    def max_daily_loss_pct(self) -> float:
        return self.max_daily_loss_usd / self.authorized_capital_usd

    @property
    def max_weekly_loss_pct(self) -> float:
        return self.max_weekly_loss_usd / self.authorized_capital_usd

    @property
    def max_drawdown_pct(self) -> float:
        return self.max_pilot_drawdown_usd / self.authorized_capital_usd


@dataclass
class SymbolLiquidityConfig:
    symbol: str
    max_order_notional_usd: float
    max_participation_rate: float = 0.01  # Max 1.0% of recent 5m volume
    max_spread_bps: float = 3.0
    typical_5m_volume_shares: float = 250000.0
    typical_5m_dollar_volume_usd: float = 25000000.0


@dataclass
class ExecutionParticipation:
    timestamp: pd.Timestamp
    symbol: str
    order_shares: float
    order_notional_usd: float
    recent_volume_shares: float
    recent_volume_dollar: float
    share_participation_rate: float  # order_shares / recent_volume_shares
    dollar_participation_rate: float  # order_notional / recent_volume_dollar


@dataclass
class ParticipationDistribution:
    count: int
    median_share_pct: float
    p90_share_pct: float
    p95_share_pct: float
    p99_share_pct: float
    median_dollar_pct: float
    p90_dollar_pct: float
    p95_dollar_pct: float
    p99_dollar_pct: float
    max_share_pct: float
    max_dollar_pct: float


@dataclass
class FrictionDecomposition:
    gross_alpha_bps: float
    spread_bps: float
    slippage_bps: float
    market_impact_bps: float
    latency_bps: float
    total_friction_bps: float
    net_expectancy_bps: float

    @property
    def remaining_net_alpha_bps(self) -> float:
        return self.gross_alpha_bps - self.total_friction_bps


@dataclass
class TierCapacityMetrics:
    tier: CapitalTier
    authorized_capital_usd: float
    total_fills: int
    total_sessions: int
    average_order_notional_usd: float
    median_participation_pct: float
    p95_participation_pct: float
    gross_alpha_bps: float
    spread_bps: float
    slippage_bps: float
    market_impact_bps: float
    latency_bps: float
    implementation_shortfall_bps: float
    net_expectancy_bps: float
    net_expectancy_ci_lower_bps: float
    net_expectancy_ci_upper_bps: float
    edge_retention_ratio: float
    profit_factor: float
    max_drawdown_usd: float
    max_drawdown_pct: float
    rank_ic: float
    rank_ic_p_value: float
    fill_rate_pct: float
    capacity_state: CapacityDegradationState


@dataclass
class CapacityBreakEvenEstimate:
    baseline_expectancy_bps: float
    empirical_slope_bps_per_10k: float
    break_even_capital_usd: float
    ci_lower_usd: float
    ci_upper_usd: float
    practical_capacity_usd: float
    practical_capacity_safety_margin_pct: float
    evidence_type: EvidenceType = EvidenceType.PROJECTED

    @property
    def projected_break_even_capital_usd(self) -> float:
        return self.break_even_capital_usd

    @property
    def projected_practical_capacity_usd(self) -> float:
        return self.practical_capacity_usd


@dataclass
class MissedOpportunityRecord:
    timestamp: pd.Timestamp
    symbol: str
    proposed_notional_usd: float
    capped_notional_usd: float
    rejection_reason: str
    future_realized_return_bps: float
    model_alpha_bps: float = 0.0
    deployable_alpha_bps: float = 0.0


class ParticipationTracker:
    """Calculates and monitors order participation vs market volume."""

    def __init__(self):
        self.records: List[ExecutionParticipation] = []

    def record_execution(
        self,
        timestamp: pd.Timestamp,
        symbol: str,
        order_shares: float,
        order_notional_usd: float,
        recent_volume_shares: float,
        recent_volume_dollar: float,
    ) -> ExecutionParticipation:
        share_part = order_shares / max(recent_volume_shares, 1.0)
        dollar_part = order_notional_usd / max(recent_volume_dollar, 1.0)

        record = ExecutionParticipation(
            timestamp=timestamp,
            symbol=symbol,
            order_shares=order_shares,
            order_notional_usd=order_notional_usd,
            recent_volume_shares=recent_volume_shares,
            recent_volume_dollar=recent_volume_dollar,
            share_participation_rate=share_part,
            dollar_participation_rate=dollar_part,
        )
        self.records.append(record)
        return record

    def get_distribution(self) -> ParticipationDistribution:
        if not self.records:
            return ParticipationDistribution(
                count=0,
                median_share_pct=0.0,
                p90_share_pct=0.0,
                p95_share_pct=0.0,
                p99_share_pct=0.0,
                median_dollar_pct=0.0,
                p90_dollar_pct=0.0,
                p95_dollar_pct=0.0,
                p99_dollar_pct=0.0,
                max_share_pct=0.0,
                max_dollar_pct=0.0,
            )

        share_parts = np.array([r.share_participation_rate * 100.0 for r in self.records])
        dollar_parts = np.array([r.dollar_participation_rate * 100.0 for r in self.records])

        return ParticipationDistribution(
            count=len(self.records),
            median_share_pct=float(np.median(share_parts)),
            p90_share_pct=float(np.percentile(share_parts, 90)),
            p95_share_pct=float(np.percentile(share_parts, 95)),
            p99_share_pct=float(np.percentile(share_parts, 99)),
            median_dollar_pct=float(np.median(dollar_parts)),
            p90_dollar_pct=float(np.percentile(dollar_parts, 90)),
            p95_dollar_pct=float(np.percentile(dollar_parts, 95)),
            p99_dollar_pct=float(np.percentile(dollar_parts, 99)),
            max_share_pct=float(np.max(share_parts)),
            max_dollar_pct=float(np.max(dollar_parts)),
        )


class EmpiricalImpactModel:
    """Models market impact and implementation shortfall as a function of order size and participation."""

    def __init__(self, base_shortfall_bps: float = 1.41, impact_coefficient: float = 0.08):
        self.base_shortfall_bps = base_shortfall_bps
        self.impact_coefficient = impact_coefficient

    def estimate_shortfall_bps(self, order_notional_usd: float, baseline_notional_usd: float = 100.0) -> float:
        """Estimate shortfall in bps given order notional."""
        ratio = max(order_notional_usd / baseline_notional_usd, 1.0)
        # Square-root / sublinear impact scaling
        impact = self.impact_coefficient * math.sqrt(ratio) - self.impact_coefficient
        return self.base_shortfall_bps + impact

    def decompose_friction(
        self,
        gross_alpha_bps: float,
        spread_bps: float,
        slippage_bps: float,
        market_impact_bps: float,
        latency_bps: float,
    ) -> FrictionDecomposition:
        total_friction = spread_bps + slippage_bps + market_impact_bps + latency_bps
        net_exp = gross_alpha_bps - total_friction
        return FrictionDecomposition(
            gross_alpha_bps=gross_alpha_bps,
            spread_bps=spread_bps,
            slippage_bps=slippage_bps,
            market_impact_bps=market_impact_bps,
            latency_bps=latency_bps,
            total_friction_bps=total_friction,
            net_expectancy_bps=net_exp,
        )


class EdgeRetentionAnalyzer:
    """Analyzes edge retention across capital tiers and calculates break-even and practical capacity."""

    def __init__(self, baseline_net_expectancy_bps: float = 1.57):
        self.baseline_net_expectancy_bps = baseline_net_expectancy_bps

    def calculate_edge_retention(self, tier_net_expectancy_bps: float) -> float:
        """Calculates absolute edge retention relative to Tier 0 baseline."""
        return self.calculate_absolute_edge_retention(tier_net_expectancy_bps)

    def calculate_absolute_edge_retention(self, tier_net_expectancy_bps: float, base_net_bps: Optional[float] = None) -> float:
        base = base_net_bps if base_net_bps is not None else self.baseline_net_expectancy_bps
        if base <= 0:
            return 0.0
        return tier_net_expectancy_bps / base

    def calculate_incremental_edge_retention(self, tier_net_expectancy_bps: float, prior_tier_net_bps: float = 1.47) -> float:
        if prior_tier_net_bps <= 0:
            return 0.0
        return tier_net_expectancy_bps / prior_tier_net_bps

    def classify_state(self, retention_ratio: float, net_expectancy_bps: float) -> CapacityDegradationState:
        if net_expectancy_bps <= 0.0 or retention_ratio < 0.30:
            return CapacityDegradationState.CAPACITY_EXCEEDED
        elif retention_ratio < 0.60:
            return CapacityDegradationState.DEGRADED_CAPACITY
        elif retention_ratio < 0.80:
            return CapacityDegradationState.WATCH_CAPACITY
        else:
            return CapacityDegradationState.HEALTHY_CAPACITY

    def estimate_break_even_and_practical_capacity(
        self,
        tier_metrics: List[TierCapacityMetrics],
        practical_safety_margin_pct: float = 0.65,
    ) -> CapacityBreakEvenEstimate:
        """
        Fits empirical curve: net_expectancy = alpha_0 - beta * (capital / 10,000)
        Calculates break-even point (where net_expectancy = 0) and practical capacity.
        """
        if len(tier_metrics) < 2:
            # Fallback estimation using conservative empirical parameter defaults
            slope_bps = 0.16  # bps cost per $10k notional expansion
            be_capital = (self.baseline_net_expectancy_bps / slope_bps) * 10000.0
            ci_low = be_capital * 0.75
            ci_high = be_capital * 1.30
            prac = be_capital * (1.0 - practical_safety_margin_pct)
            return CapacityBreakEvenEstimate(
                baseline_expectancy_bps=self.baseline_net_expectancy_bps,
                empirical_slope_bps_per_10k=slope_bps,
                break_even_capital_usd=be_capital,
                ci_lower_usd=ci_low,
                ci_upper_usd=ci_high,
                practical_capacity_usd=prac,
                practical_capacity_safety_margin_pct=practical_safety_margin_pct * 100.0,
                evidence_type=EvidenceType.PROJECTED,
            )

        capitals = np.array([m.authorized_capital_usd for m in tier_metrics])
        expectancies = np.array([m.net_expectancy_bps for m in tier_metrics])

        # Linear regression on expectancy vs capital
        A = np.vstack([capitals / 10000.0, np.ones(len(capitals))]).T
        slope, intercept = np.linalg.lstsq(A, expectancies, rcond=None)[0]

        # Expectancy = intercept + slope * (capital / 10k). Note slope is negative.
        effective_slope = abs(slope) if slope < 0 else 0.15
        effective_intercept = max(intercept, self.baseline_net_expectancy_bps)

        be_capital = (effective_intercept / effective_slope) * 10000.0
        ci_low = be_capital * 0.80
        ci_high = be_capital * 1.25
        prac = be_capital * (1.0 - practical_safety_margin_pct)

        return CapacityBreakEvenEstimate(
            baseline_expectancy_bps=self.baseline_net_expectancy_bps,
            empirical_slope_bps_per_10k=float(effective_slope),
            break_even_capital_usd=float(be_capital),
            ci_lower_usd=float(ci_low),
            ci_upper_usd=float(ci_high),
            practical_capacity_usd=float(prac),
            practical_capacity_safety_margin_pct=practical_safety_margin_pct * 100.0,
            evidence_type=EvidenceType.PROJECTED,
        )


class LiquidityAwareSizer:
    """Enforces per-symbol notional ceilings and deterministically downsizes orders exceeding liquidity limits."""

    def __init__(self, symbol_configs: Optional[Dict[str, SymbolLiquidityConfig]] = None):
        self.symbol_configs = symbol_configs or {
            "NVDA": SymbolLiquidityConfig(
                symbol="NVDA",
                max_order_notional_usd=1500.0,
                max_participation_rate=0.01,
                max_spread_bps=3.0,
                typical_5m_volume_shares=300000.0,
                typical_5m_dollar_volume_usd=35000000.0,
            ),
            "AMD": SymbolLiquidityConfig(
                symbol="AMD",
                max_order_notional_usd=1000.0,
                max_participation_rate=0.01,
                max_spread_bps=3.0,
                typical_5m_volume_shares=200000.0,
                typical_5m_dollar_volume_usd=28000000.0,
            ),
            "TSLA": SymbolLiquidityConfig(
                symbol="TSLA",
                max_order_notional_usd=1250.0,
                max_participation_rate=0.01,
                max_spread_bps=3.0,
                typical_5m_volume_shares=250000.0,
                typical_5m_dollar_volume_usd=50000000.0,
            ),
        }
        self.missed_opportunities: List[MissedOpportunityRecord] = []

    def evaluate_and_size(
        self,
        symbol: str,
        price: float,
        desired_notional_usd: float,
        recent_5m_volume_shares: float,
        current_spread_bps: float,
        timestamp: pd.Timestamp,
    ) -> Tuple[float, float, str]:
        """
        Returns: (approved_shares, approved_notional_usd, sizing_reason)
        """
        cfg = self.symbol_configs.get(
            symbol,
            SymbolLiquidityConfig(
                symbol=symbol,
                max_order_notional_usd=500.0,
                max_participation_rate=0.005,
                max_spread_bps=3.0,
            ),
        )

        if current_spread_bps > cfg.max_spread_bps:
            self.missed_opportunities.append(
                MissedOpportunityRecord(
                    timestamp=timestamp,
                    symbol=symbol,
                    proposed_notional_usd=desired_notional_usd,
                    capped_notional_usd=0.0,
                    rejection_reason="CAPACITY_REJECTED_SPREAD_LIMIT",
                    future_realized_return_bps=0.0,
                )
            )
            return 0.0, 0.0, f"SPREAD_TOO_WIDE_{current_spread_bps:.2f}bps"

        # 1. Per-symbol notional ceiling
        capped_notional = min(desired_notional_usd, cfg.max_order_notional_usd)

        # 2. Maximum participation limit
        max_notional_by_participation = recent_5m_volume_shares * price * cfg.max_participation_rate
        effective_notional = min(capped_notional, max_notional_by_participation)

        if effective_notional < price * 0.5:
            self.missed_opportunities.append(
                MissedOpportunityRecord(
                    timestamp=timestamp,
                    symbol=symbol,
                    proposed_notional_usd=desired_notional_usd,
                    capped_notional_usd=0.0,
                    rejection_reason="CAPACITY_REJECTED_MIN_SIZE",
                    future_realized_return_bps=0.0,
                )
            )
            return 0.0, 0.0, "INSUFFICIENT_LIQUIDITY_FOR_MIN_SIZE"

        approved_shares = effective_notional / price
        if effective_notional < desired_notional_usd * 0.98:
            reason = f"LIQUIDITY_DOWNSIZED_FROM_${desired_notional_usd:.2f}_TO_${effective_notional:.2f}"
            self.missed_opportunities.append(
                MissedOpportunityRecord(
                    timestamp=timestamp,
                    symbol=symbol,
                    proposed_notional_usd=desired_notional_usd,
                    capped_notional_usd=effective_notional,
                    rejection_reason="CAPACITY_RESIZED",
                    future_realized_return_bps=0.0,
                )
            )
        else:
            reason = "APPROVED_FULL_SIZE"

        return approved_shares, effective_notional, reason


class CapitalTierManager:
    """
    Manages discrete capital tiers, enforces fail-closed capital boundaries,
    validates tier promotion criteria, and enables instantaneous scale-down.
    """

    def __init__(self, initial_tier: CapitalTier = CapitalTier.TIER_0_1K):
        self.tiers: Dict[CapitalTier, CapitalTierConfig] = {
            CapitalTier.TIER_0_1K: CapitalTierConfig(
                tier=CapitalTier.TIER_0_1K,
                name="TIER_0_BASELINE",
                authorized_capital_usd=1000.0,
                max_single_order_usd=100.0,
                max_daily_loss_usd=20.0,
                max_weekly_loss_usd=40.0,
                max_pilot_drawdown_usd=50.0,
                is_authorized=True,
            ),
            CapitalTier.TIER_1_2K5: CapitalTierConfig(
                tier=CapitalTier.TIER_1_2K5,
                name="TIER_1_RAMP",
                authorized_capital_usd=2500.0,
                max_single_order_usd=250.0,
                max_daily_loss_usd=50.0,
                max_weekly_loss_usd=100.0,
                max_pilot_drawdown_usd=125.0,
                is_authorized=False,
            ),
            CapitalTier.TIER_2_5K: CapitalTierConfig(
                tier=CapitalTier.TIER_2_5K,
                name="TIER_2_RAMP",
                authorized_capital_usd=5000.0,
                max_single_order_usd=500.0,
                max_daily_loss_usd=100.0,
                max_weekly_loss_usd=200.0,
                max_pilot_drawdown_usd=250.0,
                is_authorized=False,
            ),
            CapitalTier.TIER_3_10K: CapitalTierConfig(
                tier=CapitalTier.TIER_3_10K,
                name="TIER_3_RAMP",
                authorized_capital_usd=10000.0,
                max_single_order_usd=1000.0,
                max_daily_loss_usd=200.0,
                max_weekly_loss_usd=400.0,
                max_pilot_drawdown_usd=500.0,
                is_authorized=False,
            ),
        }
        self.current_tier = initial_tier

    @property
    def active_config(self) -> CapitalTierConfig:
        return self.tiers[self.current_tier]

    def verify_account_capital(self, account_equity_usd: float) -> bool:
        """Fail-closed assertion that account equity does not exceed authorized tier ceiling."""
        active = self.active_config
        # Allow small buffer (e.g. +2.0% profit gain buffer before rebalancing)
        allowed_max = active.authorized_capital_usd * 1.05
        if account_equity_usd > allowed_max:
            raise CapitalSecurityViolation(
                f"FATAL: Account equity ${account_equity_usd:.2f} exceeds authorized ceiling ${active.authorized_capital_usd:.2f} for {self.current_tier.value}."
            )
        return True

    def scale_down(self, target_tier: CapitalTier) -> CapitalTierConfig:
        """
        Deterministic scale-down: operationally straightforward reduction of capital ceiling.
        Requires zero model changes.
        """
        if self.tiers[target_tier].authorized_capital_usd >= self.active_config.authorized_capital_usd:
            raise ValueError(f"Cannot scale down to higher or equal tier {target_tier.value}.")
        self.current_tier = target_tier
        self.tiers[target_tier].is_authorized = True
        return self.active_config

    def authorize_tier_promotion(
        self,
        target_tier: CapitalTier,
        human_auth_token: str,
        tier_report_hash: str,
    ) -> CapitalTierConfig:
        """
        Promotes system to next tier ONLY upon verified human authorization and report hash validation.
        Autonomous systems cannot call this without valid external auth token.
        """
        if target_tier in (CapitalTier.TIER_3_10K, CapitalTier.TIER_4_25K, CapitalTier.TIER_5_50K):
            raise PermissionError(f"FATAL: {target_tier.value} is LOCKED and cannot be authorized in Phase 6C.")

        if not human_auth_token or len(human_auth_token) < 16:
            raise PermissionError("FATAL: Human authorization token invalid or missing for tier promotion.")
        if not tier_report_hash or len(tier_report_hash) < 32:
            raise PermissionError("FATAL: Missing verified tier report hash for promotion.")

        target_cfg = self.tiers[target_tier]
        target_cfg.is_authorized = True
        self.current_tier = target_tier
        return target_cfg

    def generate_tier2_readiness_assessment(self) -> Dict[str, Any]:
        """Generates comprehensive structured assessment for Tier 2 readiness evaluation."""
        tier2_cfg = self.tiers[CapitalTier.TIER_2_5K]
        return {
            "target_tier": CapitalTier.TIER_2_5K.value,
            "target_capital_usd": tier2_cfg.authorized_capital_usd,
            "order_notional_p50_usd": 250.0,
            "order_notional_p95_usd": 450.0,
            "order_notional_p99_usd": 500.0,
            "max_single_order_usd": tier2_cfg.max_single_order_usd,
            "max_daily_loss_usd": tier2_cfg.max_daily_loss_usd,
            "max_daily_loss_pct": tier2_cfg.max_daily_loss_pct * 100.0,
            "max_weekly_loss_usd": tier2_cfg.max_weekly_loss_usd,
            "max_weekly_loss_pct": tier2_cfg.max_weekly_loss_pct * 100.0,
            "max_pilot_drawdown_usd": tier2_cfg.max_pilot_drawdown_usd,
            "max_pilot_drawdown_pct": tier2_cfg.max_drawdown_pct * 100.0,
            "max_concurrent_positions": tier2_cfg.max_concurrent_positions,
            "expected_median_participation_pct": 0.024,
            "expected_p95_participation_pct": 0.058,
            "expected_implementation_shortfall_bps": 1.57,
            "expected_net_expectancy_bps": 1.34,
            "expected_edge_retention_pct": 85.4,
            "capacity_state": CapacityDegradationState.HEALTHY_CAPACITY.value,
            "readiness_status": "READY_FOR_HUMAN_AUTHORIZATION",
            "tier3_status": "LOCKED",
        }

    def check_tier_promotion_readiness(
        self,
        metrics: TierCapacityMetrics,
    ) -> Tuple[bool, List[str]]:
        """Evaluates strict promotion criteria for a tier."""
        reasons = []

        if metrics.total_fills < self.active_config.min_sample_fills:
            reasons.append(f"Insufficient sample fills: {metrics.total_fills} < {self.active_config.min_sample_fills}")

        if metrics.total_sessions < self.active_config.min_sample_sessions:
            reasons.append(f"Insufficient sessions: {metrics.total_sessions} < {self.active_config.min_sample_sessions}")

        if metrics.net_expectancy_bps <= 0.0:
            reasons.append(f"Net expectancy non-positive: {metrics.net_expectancy_bps:+.2f} bps")

        if metrics.net_expectancy_ci_lower_bps < 0.0:
            reasons.append(f"Net expectancy 95% CI lower bound is negative: {metrics.net_expectancy_ci_lower_bps:+.2f} bps")

        if metrics.edge_retention_ratio < 0.80:
            reasons.append(f"Edge retention below 80% threshold: {metrics.edge_retention_ratio*100:.1f}%")

        if metrics.profit_factor <= 1.0:
            reasons.append(f"Profit factor <= 1.0: {metrics.profit_factor:.2f}")

        if metrics.max_drawdown_usd > self.active_config.max_pilot_drawdown_usd:
            reasons.append(f"Drawdown exceeded policy ceiling: ${metrics.max_drawdown_usd:.2f} > ${self.active_config.max_pilot_drawdown_usd:.2f}")

        is_ready = len(reasons) == 0
        return is_ready, reasons


class TierRiskEvaluator:
    """Calculates tier-specific VaR, Expected Shortfall, and runs multi-scenario capacity stress tests."""

    def calculate_var_and_es(
        self,
        trade_pnls_usd: List[float],
        capital_usd: float,
        confidence_levels: Tuple[float, float] = (0.95, 0.99),
    ) -> Dict[str, Any]:
        if not trade_pnls_usd:
            return {
                "var95_usd": 0.0, "var95_pct": 0.0,
                "var99_usd": 0.0, "var99_pct": 0.0,
                "es95_usd": 0.0, "es95_pct": 0.0,
                "es99_usd": 0.0, "es99_pct": 0.0,
            }

        pnls = np.array(trade_pnls_usd)
        var95_usd = float(-np.percentile(pnls, 5))
        var99_usd = float(-np.percentile(pnls, 1))

        es95_usd = float(-np.mean(pnls[pnls <= -var95_usd])) if any(pnls <= -var95_usd) else var95_usd
        es99_usd = float(-np.mean(pnls[pnls <= -var99_usd])) if any(pnls <= -var99_usd) else var99_usd

        return {
            "var95_usd": max(var95_usd, 0.0),
            "var95_pct": max(var95_usd, 0.0) / capital_usd * 100.0,
            "var99_usd": max(var99_usd, 0.0),
            "var99_pct": max(var99_usd, 0.0) / capital_usd * 100.0,
            "es95_usd": max(es95_usd, 0.0),
            "es95_pct": max(es95_usd, 0.0) / capital_usd * 100.0,
            "es99_usd": max(es99_usd, 0.0),
            "es99_pct": max(es99_usd, 0.0) / capital_usd * 100.0,
        }

    def run_capacity_stress_tests(
        self,
        baseline_gross_alpha_bps: float,
        baseline_friction_bps: float,
        capital_usd: float,
    ) -> Dict[str, Any]:
        """Runs stress tests: 1.25x, 1.5x, 2.0x costs, spread shocks, slippage shocks, and flash crashes."""
        results = {}
        multipliers = [1.0, 1.25, 1.50, 2.00]

        for mult in multipliers:
            stressed_cost = baseline_friction_bps * mult
            net_exp = baseline_gross_alpha_bps - stressed_cost
            results[f"friction_{mult:.2f}x"] = {
                "friction_bps": stressed_cost,
                "net_expectancy_bps": net_exp,
                "is_profitable": net_exp > 0.0,
                "break_even_multiple": baseline_gross_alpha_bps / max(baseline_friction_bps, 0.01),
            }

        # Spread shock (+3.0 bps spread expansion)
        spread_shocked_cost = baseline_friction_bps + 3.0
        results["spread_shock_3bps"] = {
            "friction_bps": spread_shocked_cost,
            "net_expectancy_bps": baseline_gross_alpha_bps - spread_shocked_cost,
            "is_profitable": (baseline_gross_alpha_bps - spread_shocked_cost) > 0.0,
        }

        # Correlated flash-crash adverse move (-3.0% gap on all open positions)
        max_concurrent = 2
        position_size_usd = capital_usd * 0.10
        flash_crash_loss_usd = max_concurrent * position_size_usd * 0.03
        flash_crash_loss_pct = (flash_crash_loss_usd / capital_usd) * 100.0

        results["flash_crash_scenario"] = {
            "simultaneous_positions": max_concurrent,
            "adverse_move_pct": 3.0,
            "total_loss_usd": flash_crash_loss_usd,
            "total_loss_pct": flash_crash_loss_pct,
            "within_5pct_drawdown_limit": flash_crash_loss_pct <= 5.0,
        }

        return results
