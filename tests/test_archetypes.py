"""Tests for security archetype analyzer and symbol profiling."""

import pandas as pd
import pytest

from src.data.loader import HistoricalDataLoader
from src.features.engine import FeatureEngine
from src.evaluation.archetypes import SecurityArchetypeAnalyzer, SymbolProfile


def test_symbol_profiling_and_archetype_assignment() -> None:
    nvda = HistoricalDataLoader.generate_synthetic_5m_data(symbol="NVDA", num_days=3, annualized_volatility=0.45, seed=1)
    spy = HistoricalDataLoader.generate_synthetic_5m_data(symbol="SPY", num_days=3, annualized_volatility=0.15, seed=2)
    jnj = HistoricalDataLoader.generate_synthetic_5m_data(symbol="JNJ", num_days=3, annualized_volatility=0.12, seed=3)

    eng = FeatureEngine()
    f_nvda = eng.compute_all_features(nvda)
    f_jnj = eng.compute_all_features(jnj)

    prof_nvda = SecurityArchetypeAnalyzer.profile_symbol(f_nvda, spy_df=spy, sector="technology")
    prof_jnj = SecurityArchetypeAnalyzer.profile_symbol(f_jnj, spy_df=spy, sector="healthcare")

    assert prof_nvda.symbol == "NVDA"
    assert prof_nvda.annualized_volatility_pct > 25.0
    assert prof_jnj.symbol == "JNJ"
    assert prof_jnj.annualized_volatility_pct < 25.0

    table = SecurityArchetypeAnalyzer.evaluate_archetype_generalization([prof_nvda, prof_jnj])
    assert len(table) >= 1
    assert "mean_volatility_pct" in table.columns
