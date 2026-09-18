#!/bin/bash -l
#SBATCH --job-name=mm_cpu_backtest
#SBATCH --partition=uri-cpu,cpu
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=logs/backtest_%j.out
#SBATCH --error=logs/backtest_%j.err

set -euo pipefail

export PROJECT_ROOT="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
cd "$PROJECT_ROOT"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate "/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"

echo "Node: $(hostname) | Job ID: $SLURM_JOB_ID | CPUs: $SLURM_CPUS_PER_TASK"

EXPERIMENT_ID="${EXPERIMENT_ID:-EXP_BACKTEST_$(date +%Y%m%d_%H%M%S)}"
CONFIG_PATH="${CONFIG_PATH:-configs/research_backtest.yaml}"
OUTPUT_DIR="$PROJECT_ROOT/outputs/$EXPERIMENT_ID"
mkdir -p "$OUTPUT_DIR"

python3 -m src.research.runners.run_backtest \
    --config "$CONFIG_PATH" \
    --experiment-id "$EXPERIMENT_ID" \
    --output-dir "$OUTPUT_DIR"
