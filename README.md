# Moneymaker: Quantitative Investing Research & Systematic Platform

Moneymaker is a scientific, reproducible quantitative research and paper-trading platform engineered to test whether machine-learning models, quantitative signals, and market-regime context can discover persistent risk-adjusted alpha on strictly unseen data after accounting for transaction costs, slippage, latency, and uncertainty.

## Core Philosophy
1. **Scientific Rigor**: "NO TRADE" is a first-class prediction. Avoid over-fitting and multiple-testing fallacy.
2. **Deterministic Risk**: Risk management rules are strictly deterministic and operate outside statistical models.
3. **No Future Leakage**: Every feature has explicit `event_timestamp` and `available_timestamp` coordinates.
4. **Friction-Aware**: Every strategy is audited before and after spreads, slippage, and commissions.
5. **Simulated Capital Only**: Initial portfolio is strictly $1,000 virtual capital. No live money execution in V1.

## Quick Start
```bash
# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Run the test suite
pytest -v
```

## Platform Architecture
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full architectural blueprints.
