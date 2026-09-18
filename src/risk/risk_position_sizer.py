"""
Master Risk-Based Position Sizer (Phase D).

Converts candidate trade opportunities into safe, economically optimal position sizes
based on risk budgets, dynamic stop distances, volatility, capacity limits,
drawdown throttling, and capital-tier firewalls.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

from src.risk.portfolio_risk_state import PortfolioRiskState
from src.risk.drawdown_state import DrawdownThrottleEngine, AccountRiskState
from src.risk.risk_budget import DynamicRiskBudgetModel, RiskBudgetCalculation
from src.risk.capital_tiers import get_tier_for_equity, CapitalTierConstraints
from src.execution.capacity_model import CapacityModel, CapacityAssessment, CapacityState
from src.execution.position_rounding import PositionRoundingEngine, ShareRoundingResult


class SizingDecision(str, Enum):
    SIZE_APPROVED = "SIZE_APPROVED"
    SIZE_REDUCED = "SIZE_REDUCED"
    NO_POSITION = "NO_POSITION"


@dataclass(frozen=True)
class PositionSizingDecision:
    symbol: str
    decision: SizingDecision
    target_dollars: float
    target_shares: float
    risk_dollars: float
    risk_pct_equity: float
    stop_distance_pct: float
    expected_net_edge_bps: float
    estimated_execution_cost_bps: float
    capacity_limit_dollars: float
    exposure_limit_dollars: float
    final_allowed_dollars: float
    rounding_result: ShareRoundingResult
    capacity_assessment: CapacityAssessment
    reason_codes: List[str]
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_approved(self) -> bool:
        return self.decision in (SizingDecision.SIZE_APPROVED, SizingDecision.SIZE_REDUCED) and self.target_shares > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "decision": self.decision.value,
            "target_dollars": round(self.target_dollars, 2),
            "target_shares": self.target_shares,
            "risk_dollars": round(self.risk_dollars, 2),
            "risk_pct_equity": round(self.risk_pct_equity, 4),
            "stop_distance_pct": round(self.stop_distance_pct, 4),
            "expected_net_edge_bps": round(self.expected_net_edge_bps, 2),
            "estimated_execution_cost_bps": round(self.estimated_execution_cost_bps, 2),
            "capacity_limit_dollars": round(self.capacity_limit_dollars, 2),
            "exposure_limit_dollars": round(self.exposure_limit_dollars, 2),
            "final_allowed_dollars": round(self.final_allowed_dollars, 2),
            "reason_codes": self.reason_codes,
            "is_approved": self.is_approved,
        }


class RiskPositionSizer:
    """
    Deterministic capital allocation and position-sizing engine.
    """
    def __init__(
        self,
        risk_budget_model: Optional[DynamicRiskBudgetModel] = None,
        drawdown_engine: Optional[DrawdownThrottleEngine] = None,
        capacity_model: Optional[CapacityModel] = None,
        rounding_engine: Optional[PositionRoundingEngine] = None,
    ):
        self.risk_budget_model = risk_budget_model or DynamicRiskBudgetModel()
        self.drawdown_engine = drawdown_engine or DrawdownThrottleEngine()
        self.capacity_model = capacity_model or CapacityModel()
        self.rounding_engine = rounding_engine or PositionRoundingEngine(allow_fractional=False)

    def size_position(
        self,
        portfolio_state: PortfolioRiskState,
        symbol: str,
        share_price: float,
        intraday_vol_bps: float,
        adv_dollars_30d: float,
        minute_dollar_volume: Optional[float] = None,
        predicted_net_edge_bps: float = 25.0,
        model_confidence: float = 0.60,
        event_risk_multiplier: float = 1.0,
        market_regime_multiplier: float = 1.0,
        recent_mae_pct: Optional[float] = None,
        sector: str = "UNKNOWN",
    ) -> PositionSizingDecision:
        """
        Executes complete risk-based sizing calculation.
        """
        reason_codes: List[str] = []

        # 1. Fail-Closed Check on Essential Inputs
        if (
            portfolio_state is None
            or portfolio_state.current_equity <= 0.0
            or share_price <= 0.0
            or intraday_vol_bps <= 0.0
            or adv_dollars_30d <= 0.0
            or event_risk_multiplier <= 0.0
        ):
            reason_codes.append("MISSING_OR_INVALID_INPUTS_FAIL_CLOSED")
            return self._build_rejection(
                symbol=symbol,
                share_price=share_price,
                reasons=reason_codes,
                net_edge=predicted_net_edge_bps,
            )

        # 2. Drawdown State Machine Check
        throttle = self.drawdown_engine.evaluate(portfolio_state)
        reason_codes.extend(throttle.reason_codes)
        if not throttle.is_trading_allowed or throttle.risk_budget_multiplier <= 0.0:
            reason_codes.append(f"DRAWDOWN_THROTTLE_{throttle.risk_state.value}")
            return self._build_rejection(
                symbol=symbol,
                share_price=share_price,
                reasons=reason_codes,
                net_edge=predicted_net_edge_bps,
            )

        # 3. Capital Tier Firewalls & Position Count Limits
        tier = get_tier_for_equity(portfolio_state.current_equity)
        if portfolio_state.active_position_count >= tier.max_open_positions:
            # If we already have max open positions (unless symbol is already active)
            if symbol not in portfolio_state.open_positions:
                reason_codes.append(f"MAX_OPEN_POSITIONS_REACHED_{tier.max_open_positions}")
                return self._build_rejection(
                    symbol=symbol,
                    share_price=share_price,
                    reasons=reason_codes,
                    net_edge=predicted_net_edge_bps,
                )

        # 4. Compute Dynamic Risk Budget & Raw Position Size
        budget_calc: RiskBudgetCalculation = self.risk_budget_model.compute_risk_budget(
            current_equity=portfolio_state.current_equity,
            intraday_vol_bps=intraday_vol_bps,
            predicted_net_edge_bps=predicted_net_edge_bps,
            model_confidence=model_confidence,
            recent_mae_pct=recent_mae_pct,
        )

        # Apply drawdown throttle, event risk, and market regime multipliers
        effective_risk_dollars = (
            budget_calc.final_allowed_risk_dollars
            * throttle.risk_budget_multiplier
            * event_risk_multiplier
            * market_regime_multiplier
        )
        total_risk_pct = budget_calc.effective_stop_pct + self.risk_budget_model.slippage_buffer_pct
        raw_position_dollars = effective_risk_dollars / total_risk_pct

        # 5. Apply Exposure & Concentration Ceilings
        max_position_dollars = portfolio_state.current_equity * tier.max_position_equity_pct
        available_cash = portfolio_state.cash
        exposure_limit = min(max_position_dollars, available_cash)

        # Sector concentration ceiling
        current_sector_exp = portfolio_state.get_sector_exposure_dollars(sector)
        max_sector_exp = portfolio_state.current_equity * tier.max_sector_equity_pct
        remaining_sector_capacity = max(0.0, max_sector_exp - current_sector_exp)
        exposure_limit = min(exposure_limit, remaining_sector_capacity)

        # 6. Apply Market Capacity & Impact Limits
        target_pre_cap = min(raw_position_dollars, exposure_limit)
        cap_assessment = self.capacity_model.estimate_capacity(
            symbol=symbol,
            target_dollars=target_pre_cap,
            adv_dollars_30d=adv_dollars_30d,
            minute_dollar_volume=minute_dollar_volume,
        )

        final_dollars = min(target_pre_cap, cap_assessment.max_safe_position_dollars)

        # 7. Check Minimum Economic Position Size
        if final_dollars < tier.min_trade_dollars:
            reason_codes.append(f"POSITION_BELOW_MINIMUM_ECONOMIC_SIZE_{tier.min_trade_dollars:.0f}")
            return self._build_rejection(
                symbol=symbol,
                share_price=share_price,
                reasons=reason_codes,
                net_edge=predicted_net_edge_bps,
                cap_assessment=cap_assessment,
            )

        # 8. Share Rounding
        rounding = self.rounding_engine.round_position(
            target_dollars=final_dollars,
            share_price=share_price,
        )

        if rounding.rounded_shares <= 0:
            reason_codes.append("SHARE_PRICE_EXCEEDS_ALLOCATED_CAPITAL_ZERO_SHARES")
            return self._build_rejection(
                symbol=symbol,
                share_price=share_price,
                reasons=reason_codes,
                net_edge=predicted_net_edge_bps,
                cap_assessment=cap_assessment,
                rounding=rounding,
            )

        actual_dollars = rounding.actual_notional_dollars
        actual_risk_dollars = actual_dollars * total_risk_pct
        actual_risk_pct = actual_risk_dollars / portfolio_state.current_equity

        # Determine Decision Label
        if actual_dollars < raw_position_dollars * 0.90:
            decision = SizingDecision.SIZE_REDUCED
            reason_codes.append("SIZE_REDUCED_BY_EXPOSURE_OR_CAPACITY_LIMITS")
        else:
            decision = SizingDecision.SIZE_APPROVED
            reason_codes.append("SIZE_APPROVED_FULL_RISK_BUDGET")

        return PositionSizingDecision(
            symbol=symbol,
            decision=decision,
            target_dollars=final_dollars,
            target_shares=rounding.rounded_shares,
            risk_dollars=actual_risk_dollars,
            risk_pct_equity=actual_risk_pct,
            stop_distance_pct=budget_calc.effective_stop_pct,
            expected_net_edge_bps=predicted_net_edge_bps,
            estimated_execution_cost_bps=cap_assessment.estimated_impact_bps,
            capacity_limit_dollars=cap_assessment.max_safe_position_dollars,
            exposure_limit_dollars=exposure_limit,
            final_allowed_dollars=actual_dollars,
            rounding_result=rounding,
            capacity_assessment=cap_assessment,
            reason_codes=reason_codes,
            diagnostics={
                "base_risk_dollars": budget_calc.base_risk_dollars,
                "vol_mult": budget_calc.volatility_multiplier,
                "edge_conf_mult": budget_calc.edge_confidence_multiplier,
                "throttle_mult": throttle.risk_budget_multiplier,
                "tier": tier.tier_name.value,
            },
        )

    def _build_rejection(
        self,
        symbol: str,
        share_price: float,
        reasons: List[str],
        net_edge: float = 0.0,
        cap_assessment: Optional[CapacityAssessment] = None,
        rounding: Optional[ShareRoundingResult] = None,
    ) -> PositionSizingDecision:
        cap = cap_assessment or CapacityAssessment(
            symbol=symbol,
            target_dollars=0.0,
            adv_dollars_30d=0.0,
            minute_dollar_volume=0.0,
            adv_participation_pct=0.0,
            minute_participation_pct=0.0,
            estimated_impact_bps=0.0,
            max_safe_position_dollars=0.0,
            is_capacity_approved=False,
            capacity_state=CapacityState.NO_CAPACITY,
        )
        rnd = rounding or ShareRoundingResult(
            target_dollars=0.0,
            share_price=share_price,
            unrounded_shares=0.0,
            rounded_shares=0.0,
            actual_notional_dollars=0.0,
            rounding_error_dollars=0.0,
            allow_fractional=False,
        )
        return PositionSizingDecision(
            symbol=symbol,
            decision=SizingDecision.NO_POSITION,
            target_dollars=0.0,
            target_shares=0.0,
            risk_dollars=0.0,
            risk_pct_equity=0.0,
            stop_distance_pct=0.0,
            expected_net_edge_bps=net_edge,
            estimated_execution_cost_bps=0.0,
            capacity_limit_dollars=0.0,
            exposure_limit_dollars=0.0,
            final_allowed_dollars=0.0,
            rounding_result=rnd,
            capacity_assessment=cap,
            reason_codes=reasons,
        )
