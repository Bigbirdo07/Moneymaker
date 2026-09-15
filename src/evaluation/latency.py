"""
Comprehensive Latency Attribution & Tracking for Phase 3A Shadow Execution.
Measures discrete latency components from exchange event through hypothetical fill.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class LatencyRecord:
    """Detailed record of all timestamps for a single decision cycle."""
    decision_id: str
    symbol: str
    exchange_timestamp: Optional[pd.Timestamp]
    provider_timestamp: Optional[pd.Timestamp]
    received_timestamp: pd.Timestamp
    feature_ready_timestamp: pd.Timestamp
    model_start_timestamp: pd.Timestamp
    model_end_timestamp: pd.Timestamp
    ranking_timestamp: pd.Timestamp
    decision_timestamp: pd.Timestamp
    hypothetical_fill_timestamp: Optional[pd.Timestamp] = None

    @property
    def exchange_to_provider_ms(self) -> Optional[float]:
        if self.exchange_timestamp and self.provider_timestamp:
            return (self.provider_timestamp - self.exchange_timestamp).total_seconds() * 1000.0
        return None

    @property
    def provider_to_receipt_ms(self) -> Optional[float]:
        if self.provider_timestamp:
            return (self.received_timestamp - self.provider_timestamp).total_seconds() * 1000.0
        return None

    @property
    def feature_computation_ms(self) -> float:
        return (self.feature_ready_timestamp - self.received_timestamp).total_seconds() * 1000.0

    @property
    def model_inference_ms(self) -> float:
        return (self.model_end_timestamp - self.model_start_timestamp).total_seconds() * 1000.0

    @property
    def ranking_ms(self) -> float:
        return (self.ranking_timestamp - self.model_end_timestamp).total_seconds() * 1000.0

    @property
    def decision_generation_ms(self) -> float:
        return (self.decision_timestamp - self.ranking_timestamp).total_seconds() * 1000.0

    @property
    def total_decision_latency_ms(self) -> float:
        """Total local processing time from data receipt to trade decision."""
        return (self.decision_timestamp - self.received_timestamp).total_seconds() * 1000.0

    @property
    def total_system_latency_ms(self) -> Optional[float]:
        """End-to-end latency from exchange event to final decision."""
        if self.exchange_timestamp:
            return (self.decision_timestamp - self.exchange_timestamp).total_seconds() * 1000.0
        return self.total_decision_latency_ms

    @property
    def execution_fill_latency_ms(self) -> Optional[float]:
        if self.hypothetical_fill_timestamp:
            return (self.hypothetical_fill_timestamp - self.decision_timestamp).total_seconds() * 1000.0
        return None


class LatencyTracker:
    """Tracks, aggregates, and benchmarks decision cycle latency against SLA limits."""

    def __init__(self, max_allowed_decision_latency_sec: float = 1.5, alpha_decay_boundary_sec: float = 90.0):
        self.max_allowed_decision_latency_sec = max_allowed_decision_latency_sec
        self.alpha_decay_boundary_sec = alpha_decay_boundary_sec
        self._records: List[LatencyRecord] = []

    def record(self, latency_record: LatencyRecord) -> None:
        self._records.append(latency_record)

    def summary(self) -> Dict[str, float]:
        """Compute percentile breakdown of total decision latency."""
        if not self._records:
            return {
                "count": 0,
                "median_decision_ms": 0.0,
                "p90_decision_ms": 0.0,
                "p95_decision_ms": 0.0,
                "p99_decision_ms": 0.0,
                "max_decision_ms": 0.0,
                "mean_feature_ms": 0.0,
                "mean_inference_ms": 0.0,
                "mean_ranking_ms": 0.0,
                "pct_below_90s_boundary": 100.0,
            }

        decision_lats = np.array([r.total_decision_latency_ms for r in self._records])
        feature_lats = np.array([r.feature_computation_ms for r in self._records])
        inference_lats = np.array([r.model_inference_ms for r in self._records])
        ranking_lats = np.array([r.ranking_ms for r in self._records])

        return {
            "count": len(self._records),
            "median_decision_ms": float(np.median(decision_lats)),
            "p90_decision_ms": float(np.percentile(decision_lats, 90)),
            "p95_decision_ms": float(np.percentile(decision_lats, 95)),
            "p99_decision_ms": float(np.percentile(decision_lats, 99)),
            "max_decision_ms": float(np.max(decision_lats)),
            "mean_feature_ms": float(np.mean(feature_lats)),
            "mean_inference_ms": float(np.mean(inference_lats)),
            "mean_ranking_ms": float(np.mean(ranking_lats)),
            "pct_below_90s_boundary": float(np.mean(decision_lats < (self.alpha_decay_boundary_sec * 1000.0)) * 100.0),
        }
