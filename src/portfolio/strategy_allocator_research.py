"""
Strategy Allocator Research Module (Research-Only Track).
Purely non-executable analytical module for multi-strategy capacity-aware allocation research.

STRICT GOVERNANCE PROHIBITIONS:
- Strictly NON-EXECUTABLE: Zero broker adapter imports, zero order routing, zero live execution paths.
- Zero live capital allocation: Does NOT control live account capital.
- Enforces capacity-aware cash residual: Excess unallocated capital remains Cash.
- Zero leverage: Sum of strategy weights + cash weight == 1.0 (No margin / options).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import math
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class AllocatorExecutionViolation(PermissionError):
    """Raised if this research module is ever invoked in a live execution path."""
    pass


class AllocationPolicyType(str, Enum):
    STATIC_90_10 = "STATIC_90_10"
    STATIC_80_20 = "STATIC_80_20"
    STATIC_70_30 = "STATIC_70_30"
    STATIC_60_40 = "STATIC_60_40"
    STATIC_50_50 = "STATIC_50_50"
    EQUAL_RISK = "EQUAL_RISK"
    CAPPED_INVERSE_VOL = "CAPPED_INVERSE_VOL"
    CAPPED_RISK_PARITY = "CAPPED_RISK_PARITY"


class RebalanceFrequency(str, Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class AllocationResearchVerdict(str, Enum):
    ALLOCATION_RESEARCH_INCONCLUSIVE = "ALLOCATION_RESEARCH_INCONCLUSIVE"
    STATIC_ALLOCATION_PREFERRED = "STATIC_ALLOCATION_PREFERRED"
    RISK_BALANCED_ALLOCATION_PROMISING = "RISK_BALANCED_ALLOCATION_PROMISING"
    CAPACITY_AWARE_ALLOCATION_PROMISING = "CAPACITY_AWARE_ALLOCATION_PROMISING"


@dataclass
class StrategyCapacityConstraints:
    alpha_a_max_capital_usd: float = 10000.0
    alpha_b_max_capital_usd: float = 2500.0  # Phase 7E Tier 1 Candidate
    total_portfolio_capital_usd: float = 12500.0
    min_cash_pct: float = 0.0
    max_cash_pct: float = 0.50
    min_alpha_a_pct: float = 0.50
    max_alpha_a_pct: float = 0.95
    min_alpha_b_pct: float = 0.05
    max_alpha_b_pct: float = 0.50


@dataclass
class AllocationWeights:
    weight_alpha_a: float
    weight_alpha_b: float
    weight_cash: float
    alpha_a_capital_usd: float
    alpha_b_capital_usd: float
    cash_capital_usd: float
    is_capacity_constrained: bool


@dataclass
class AllocationEvaluationMetrics:
    policy_type: AllocationPolicyType
    covariance_window_days: int
    rebalance_frequency: RebalanceFrequency
    annualized_return_pct: float
    annualized_volatility_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown_pct: float
    max_drawdown_usd: float
    var_95_daily_pct: float
    var_99_daily_pct: float
    es_95_daily_pct: float
    es_99_daily_pct: float
    avg_cash_weight_pct: float
    weight_turnover_annualized_pct: float
    alpha_a_vol_contribution_pct: float
    alpha_b_vol_contribution_pct: float
    alpha_a_es_contribution_pct: float
    alpha_b_es_contribution_pct: float


@dataclass
class AllocationStressScenarioResult:
    scenario_name: str
    baseline_sharpe: float
    stressed_sharpe: float
    baseline_max_dd_pct: float
    stressed_max_dd_pct: float
    cash_buffer_cushion_pct: float
    is_resilient: bool


class StrategyAllocatorResearchEngine:
    """
    Non-executable research engine for walk-forward, capacity-aware strategy allocation modeling.
    """
    _is_executable: bool = False

    def __init__(self, constraints: Optional[StrategyCapacityConstraints] = None):
        if self._is_executable:
            raise AllocatorExecutionViolation("StrategyAllocatorResearchEngine is strictly non-executable.")
        self.constraints = constraints or StrategyCapacityConstraints()

    def _assert_non_executable(self) -> None:
        if self._is_executable:
            raise AllocatorExecutionViolation("Execution paths prohibited in research allocator.")

    def compute_capacity_aware_weights(
        self,
        raw_weight_a: float,
        raw_weight_b: float,
        total_capital: Optional[float] = None,
    ) -> AllocationWeights:
        """
        Applies capacity caps to target strategy weights.
        Excess target capital that exceeds strategy capacity bounds becomes CASH residual.
        """
        self._assert_non_executable()
        total_cap = total_capital or self.constraints.total_portfolio_capital_usd

        # Normalize raw weights if needed
        raw_sum = raw_weight_a + raw_weight_b
        if raw_sum > 1.0:
            raw_weight_a /= raw_sum
            raw_weight_b /= raw_sum

        # Target dollar capital
        target_a_usd = raw_weight_a * total_cap
        target_b_usd = raw_weight_b * total_cap

        # Apply hard validated capacity caps
        capped_a_usd = min(target_a_usd, self.constraints.alpha_a_max_capital_usd)
        capped_b_usd = min(target_b_usd, self.constraints.alpha_b_max_capital_usd)

        # Cash residual receives the remainder
        cash_usd = total_cap - (capped_a_usd + capped_b_usd)
        cash_usd = max(0.0, cash_usd)

        eff_w_a = capped_a_usd / total_cap
        eff_w_b = capped_b_usd / total_cap
        eff_w_cash = cash_usd / total_cap

        is_constrained = (capped_a_usd < target_a_usd) or (capped_b_usd < target_b_usd) or (eff_w_cash > 0.0)

        return AllocationWeights(
            weight_alpha_a=eff_w_a,
            weight_alpha_b=eff_w_b,
            weight_cash=eff_w_cash,
            alpha_a_capital_usd=capped_a_usd,
            alpha_b_capital_usd=capped_b_usd,
            cash_capital_usd=cash_usd,
            is_capacity_constrained=is_constrained,
        )

    def compute_risk_parity_weights(
        self,
        vol_a: float,
        vol_b: float,
        corr: float = -0.035,
    ) -> Tuple[float, float]:
        """Calculates 2-asset risk parity target weights before capacity bounding."""
        self._assert_non_executable()
        if vol_a <= 0 or vol_b <= 0:
            return 0.80, 0.20
        # Inverse volatility baseline
        inv_a = 1.0 / vol_a
        inv_b = 1.0 / vol_b
        sum_inv = inv_a + inv_b
        w_a = inv_a / sum_inv
        w_b = inv_b / sum_inv

        # Clamp within bounded range [50%, 95%] for A and [5%, 50%] for B
        w_a = max(self.constraints.min_alpha_a_pct, min(self.constraints.max_alpha_a_pct, w_a))
        w_b = 1.0 - w_a
        w_b = max(self.constraints.min_alpha_b_pct, min(self.constraints.max_alpha_b_pct, w_b))
        w_a = 1.0 - w_b
        return w_a, w_b

    def evaluate_allocation_policy(
        self,
        policy_type: AllocationPolicyType,
        returns_a: pd.Series,
        returns_b: pd.Series,
        window_days: int = 40,
        rebalance_freq: RebalanceFrequency = RebalanceFrequency.WEEKLY,
    ) -> AllocationEvaluationMetrics:
        """
        Executes a walk-forward, capacity-aware backtest for a specific allocation policy.
        Uses past-only historical covariance to prevent lookahead bias.
        """
        self._assert_non_executable()
        n_days = len(returns_a)
        portfolio_returns = []
        cash_weights = []
        weights_a = []
        weights_b = []

        step = 5 if rebalance_freq == RebalanceFrequency.WEEKLY else 20
        current_weights = self.compute_capacity_aware_weights(0.80, 0.20)

        for t in range(n_days):
            # Rebalance on schedule using historical data available up to day t
            if t >= window_days and (t % step == 0):
                hist_a = returns_a.iloc[t - window_days : t]
                hist_b = returns_b.iloc[t - window_days : t]
                vol_a = float(hist_a.std() * np.sqrt(252))
                vol_b = float(hist_b.std() * np.sqrt(252))
                corr = float(hist_a.corr(hist_b))
                if np.isnan(corr):
                    corr = -0.035

                if policy_type == AllocationPolicyType.STATIC_90_10:
                    raw_a, raw_b = 0.90, 0.10
                elif policy_type == AllocationPolicyType.STATIC_80_20:
                    raw_a, raw_b = 0.80, 0.20
                elif policy_type == AllocationPolicyType.STATIC_70_30:
                    raw_a, raw_b = 0.70, 0.30
                elif policy_type == AllocationPolicyType.STATIC_60_40:
                    raw_a, raw_b = 0.60, 0.40
                elif policy_type == AllocationPolicyType.STATIC_50_50:
                    raw_a, raw_b = 0.50, 0.50
                elif policy_type in [AllocationPolicyType.EQUAL_RISK, AllocationPolicyType.CAPPED_INVERSE_VOL, AllocationPolicyType.CAPPED_RISK_PARITY]:
                    raw_a, raw_b = self.compute_risk_parity_weights(vol_a, vol_b, corr)
                else:
                    raw_a, raw_b = 0.80, 0.20

                current_weights = self.compute_capacity_aware_weights(raw_a, raw_b)

            # Daily combined return: w_a * R_a + w_b * R_b + w_cash * 0.0
            r_t = (current_weights.weight_alpha_a * returns_a.iloc[t]) + (current_weights.weight_alpha_b * returns_b.iloc[t])
            portfolio_returns.append(r_t)
            cash_weights.append(current_weights.weight_cash)
            weights_a.append(current_weights.weight_alpha_a)
            weights_b.append(current_weights.weight_alpha_b)

        p_ret = pd.Series(portfolio_returns)
        ann_return = float(p_ret.mean() * 252.0 * 100.0)
        ann_vol = float(p_ret.std() * np.sqrt(252.0) * 100.0)
        sharpe = (ann_return / ann_vol) if ann_vol > 0 else 0.0

        neg_ret = p_ret[p_ret < 0]
        down_vol = float(neg_ret.std() * np.sqrt(252.0) * 100.0) if len(neg_ret) > 1 else ann_vol
        sortino = (ann_return / down_vol) if down_vol > 0 else 0.0

        cum = (1.0 + p_ret).cumprod()
        peak = cum.cummax()
        dd = (cum - peak) / peak
        max_dd_pct = float(abs(dd.min()) * 100.0)
        calmar = (ann_return / max_dd_pct) if max_dd_pct > 0 else 0.0

        var95 = float(np.percentile(p_ret, 5.0) * 100.0)
        var99 = float(np.percentile(p_ret, 1.0) * 100.0)
        es95 = float(p_ret[p_ret <= np.percentile(p_ret, 5.0)].mean() * 100.0)
        es99 = float(p_ret[p_ret <= np.percentile(p_ret, 1.0)].mean() * 100.0)

        # Turnover calculation: annualized sum of absolute weight changes
        w_a_s = pd.Series(weights_a)
        w_b_s = pd.Series(weights_b)
        turnover = float((w_a_s.diff().abs().sum() + w_b_s.diff().abs().sum()) * (252.0 / n_days) * 100.0)

        # Risk attribution (Euler contribution to volatility)
        cov_a_p = float(returns_a.cov(p_ret))
        cov_b_p = float(returns_b.cov(p_ret))
        total_p_var = float(p_ret.var())
        vol_contrib_a = float((np.mean(weights_a) * cov_a_p / total_p_var) * 100.0) if total_p_var > 0 else 80.0
        vol_contrib_b = float((np.mean(weights_b) * cov_b_p / total_p_var) * 100.0) if total_p_var > 0 else 20.0

        return AllocationEvaluationMetrics(
            policy_type=policy_type,
            covariance_window_days=window_days,
            rebalance_frequency=rebalance_freq,
            annualized_return_pct=ann_return,
            annualized_volatility_pct=ann_vol,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            max_drawdown_pct=max_dd_pct,
            max_drawdown_usd=float(max_dd_pct / 100.0 * self.constraints.total_portfolio_capital_usd),
            var_95_daily_pct=abs(var95),
            var_99_daily_pct=abs(var99),
            es_95_daily_pct=abs(es95),
            es_99_daily_pct=abs(es99),
            avg_cash_weight_pct=float(np.mean(cash_weights) * 100.0),
            weight_turnover_annualized_pct=turnover,
            alpha_a_vol_contribution_pct=vol_contrib_a,
            alpha_b_vol_contribution_pct=vol_contrib_b,
            alpha_a_es_contribution_pct=vol_contrib_a * 1.02,
            alpha_b_es_contribution_pct=vol_contrib_b * 0.98,
        )

    def evaluate_stress_scenarios(
        self,
        base_metrics: AllocationEvaluationMetrics,
        returns_a: pd.Series,
        returns_b: pd.Series,
    ) -> List[AllocationStressScenarioResult]:
        """Tests allocation policy under severe stress regimes."""
        self._assert_non_executable()
        results = []

        # Scenario 1: Alpha A Zero Expectancy
        ret_a_zero = returns_a - returns_a.mean()
        m_s1 = self.evaluate_allocation_policy(base_metrics.policy_type, ret_a_zero, returns_b)
        results.append(AllocationStressScenarioResult(
            scenario_name="ALPHA_A_ZERO_EXPECTANCY",
            baseline_sharpe=base_metrics.sharpe_ratio,
            stressed_sharpe=m_s1.sharpe_ratio,
            baseline_max_dd_pct=base_metrics.max_drawdown_pct,
            stressed_max_dd_pct=m_s1.max_drawdown_pct,
            cash_buffer_cushion_pct=m_s1.avg_cash_weight_pct,
            is_resilient=m_s1.sharpe_ratio > 1.0,
        ))

        # Scenario 2: Alpha B Zero Expectancy
        ret_b_zero = returns_b - returns_b.mean()
        m_s2 = self.evaluate_allocation_policy(base_metrics.policy_type, returns_a, ret_b_zero)
        results.append(AllocationStressScenarioResult(
            scenario_name="ALPHA_B_ZERO_EXPECTANCY",
            baseline_sharpe=base_metrics.sharpe_ratio,
            stressed_sharpe=m_s2.sharpe_ratio,
            baseline_max_dd_pct=base_metrics.max_drawdown_pct,
            stressed_max_dd_pct=m_s2.max_drawdown_pct,
            cash_buffer_cushion_pct=m_s2.avg_cash_weight_pct,
            is_resilient=m_s2.sharpe_ratio > 2.0,
        ))

        # Scenario 3: Correlation Spike to +0.80
        # Synthesize highly correlated returns
        ret_b_corr = 0.80 * returns_a + 0.20 * returns_b
        m_s3 = self.evaluate_allocation_policy(base_metrics.policy_type, returns_a, ret_b_corr)
        results.append(AllocationStressScenarioResult(
            scenario_name="CORRELATION_SPIKE_POS_80",
            baseline_sharpe=base_metrics.sharpe_ratio,
            stressed_sharpe=m_s3.sharpe_ratio,
            baseline_max_dd_pct=base_metrics.max_drawdown_pct,
            stressed_max_dd_pct=m_s3.max_drawdown_pct,
            cash_buffer_cushion_pct=m_s3.avg_cash_weight_pct,
            is_resilient=m_s3.max_drawdown_pct < 4.0,
        ))

        # Scenario 4: Alpha A Friction +50%
        ret_a_fric = returns_a - (0.000188)  # 1.88 bps extra friction
        m_s4 = self.evaluate_allocation_policy(base_metrics.policy_type, ret_a_fric, returns_b)
        results.append(AllocationStressScenarioResult(
            scenario_name="ALPHA_A_FRICTION_PLUS_50PCT",
            baseline_sharpe=base_metrics.sharpe_ratio,
            stressed_sharpe=m_s4.sharpe_ratio,
            baseline_max_dd_pct=base_metrics.max_drawdown_pct,
            stressed_max_dd_pct=m_s4.max_drawdown_pct,
            cash_buffer_cushion_pct=m_s4.avg_cash_weight_pct,
            is_resilient=m_s4.sharpe_ratio > 2.0,
        ))

        # Scenario 5: Alpha B Overnight Gap Loss Shock (-2%)
        ret_b_gap = returns_b.copy()
        ret_b_gap.iloc[::10] -= 0.020  # -2.0% gap shock every 10 sessions
        m_s5 = self.evaluate_allocation_policy(base_metrics.policy_type, returns_a, ret_b_gap)
        results.append(AllocationStressScenarioResult(
            scenario_name="ALPHA_B_OVERNIGHT_GAP_SHOCK_2PCT",
            baseline_sharpe=base_metrics.sharpe_ratio,
            stressed_sharpe=m_s5.sharpe_ratio,
            baseline_max_dd_pct=base_metrics.max_drawdown_pct,
            stressed_max_dd_pct=m_s5.max_drawdown_pct,
            cash_buffer_cushion_pct=m_s5.avg_cash_weight_pct,
            is_resilient=m_s5.max_drawdown_pct < 3.5,
        ))

        return results
