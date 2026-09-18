"""Tests for ExecutionEnvironment & Live Block (Phase F5)."""

import pytest
from src.broker.execution_environment import (
    ExecutionEnvironment,
    RealMoneyAuthorizationError,
    validate_execution_environment,
)


def test_paper_and_simulation_environments_allowed():
    # Should not raise
    validate_execution_environment(ExecutionEnvironment.SIMULATION)
    validate_execution_environment(ExecutionEnvironment.DRY_RUN)
    validate_execution_environment(ExecutionEnvironment.PAPER)


def test_live_environment_hard_blocked():
    with pytest.raises(RealMoneyAuthorizationError) as exc_info:
        validate_execution_environment(ExecutionEnvironment.LIVE)
    assert "strictly unauthorized" in str(exc_info.value)
