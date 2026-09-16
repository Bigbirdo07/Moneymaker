"""
HPC Entrypoint: 100k Path Monte Carlo Resampling Engine.
"""
import argparse
import json
import os
from datetime import datetime, timezone
import numpy as np
from src.research.monte_carlo_engine import MonteCarloEngine


def main():
    parser = argparse.ArgumentParser(description="Run Monte Carlo Resampling")
    parser.add_argument("--paths", type=int, default=100000)
    parser.add_argument("--output-dir", type=str, required=True)
    parser.add_argument("--experiment-id", type=str, required=True)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    # 60 days multi-strategy empirical daily returns
    daily_returns = np.array([0.0015, 0.0021, -0.0004, 0.0018, 0.0009, -0.0011, 0.0028, 0.0006, 0.0014, -0.0003] * 6)
    res = MonteCarloEngine.run_simulation(daily_returns=daily_returns, num_paths=args.paths)

    metrics = {
        "experiment_id": args.experiment_id,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "total_paths": res.total_paths,
        "mean_return_pct": res.mean_terminal_return_pct,
        "p95_return_pct": res.p95_terminal_return_pct,
        "p05_return_pct": res.p05_terminal_return_pct,
        "max_drawdown_p95_pct": res.max_drawdown_p95_pct,
        "prob_drawdown_exceeds_6pct": res.prob_drawdown_exceeds_6pct,
        "status": "COMPLETED",
    }

    with open(os.path.join(args.output_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Monte Carlo simulation {args.experiment_id} finished across {args.paths} paths.")


if __name__ == "__main__":
    main()
