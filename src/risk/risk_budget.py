"""
Dynamic Risk Budgeting & Stop Distance Modeling.

Computes trade risk budgets based on account equity, effective stop distances,
intraday volatility, and sub-linear edge/confidence multipliers.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
import numpy as np


@dataclass(frozen=True)
class RiskBudgetCalculation:
    base_risk_dollars: float
    effective_stop_pct: float
    volatility_multiplier: float
    edge_confidence_multiplier: float
    final_allowed_risk_dollars: float
    raw_theoretical_position_dollars: float


class DynamicRiskBudgetModel:
    """
    Computes per-trade risk dollars and effective stop distance.
    """
    def __init__(
        self,
        base_risk_pct: float = 0.0075,            # 0.75% of equity base risk budget
        min_stop_distance_pct: float = 0.010,     # 1.0% stop floor
        max_stop_distance_pct: float = 0.035,     # 3.5% maximum allowable stop
        slippage_buffer_pct: float = 0.0015,      # 15 bps slippage / gap execution buffer
        target_intraday_vol_bps: float = 120.0,   # Baseline 120 bps intraday ATR / volatility
    ):
        self.base_risk_pct = base_risk_pct
        self.min_stop_distance_pct = min_stop_distance_pct
        self.max_stop_distance_pct = max_stop_distance_pct
        self.slippage_buffer_pct = slippage_buffer_pct
        self.target_intraday_vol_bps = target_intraday_vol_bps

    def compute_effective_stop(
        self,
        intraday_vol_bps: float,
        recent_mae_pct: Optional[float] = None,
    ) -> float:
        """
        Computes dynamic effective stop distance based on realized volatility and MAE.
        """
        vol_stop = (intraday_vol_bps / 10000.0) * 1.5  # 1.5x intraday realized vol
        mae_stop = recent_mae_pct if recent_mae_pct is not None else 0.0

        effective = max(self.min_stop_distance_pct, vol_stop, mae_stop)
        return min(self.max_stop_distance_pct, effective)

    def compute_risk_budget(
        self,
        current_equity: float,
        intraday_vol_bps: float,
        predicted_net_edge_bps: float = 25.0,
        model_confidence: float = 0.60,
        recent_mae_pct: Optional[float] = None,
    ) -> RiskBudgetCalculation:
        """
        Computes comprehensive risk budget and theoretical position size.
        """
        # 1. Base Dollar Risk
        base_risk = current_equity * self.base_risk_pct

        # 2. Dynamic Effective Stop Distance
        stop_dist = self.compute_effective_stop(intraday_vol_bps, recent_mae_pct)
        total_risk_pct = stop_dist + self.slippage_buffer_pct

        # 3. Volatility Multiplier (Inverse Volatility Scaling)
        # Higher volatility stocks receive smaller multipliers to prevent excessive dollar risk
        vol_ratio = self.target_intraday_vol_bps / max(30.0, intraday_vol_bps)
        vol_mult = float(np.clip(vol_ratio, 0.60, 1.40))

        # 4. Edge & Confidence Multiplier (Sub-linear scaling, no Kelly overleveraging)
        edge_ratio = max(0.5, predicted_net_edge_bps / 25.0)
        conf_ratio = max(0.5, model_confidence / 0.60)
        raw_edge_mult = float(np.sqrt(edge_ratio) * conf_ratio)
        edge_conf_mult = float(np.clip(raw_edge_mult, 0.75, 1.25))

        # 5. Final Allowed Risk Dollars
        final_risk = base_risk * vol_mult * edge_conf_mult

        # 6. Raw Theoretical Position Size
        raw_position = final_risk / total_risk_pct

        return RiskBudgetCalculation(
            base_risk_dollars=base_risk,
            effective_stop_pct=stop_dist,
            volatility_multiplier=vol_mult,
            edge_confidence_multiplier=edge_conf_mult,
            final_allowed_risk_dollars=final_risk,
            raw_theoretical_position_dollars=raw_position,
        )
