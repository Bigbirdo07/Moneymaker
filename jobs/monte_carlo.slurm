#!/bin/bash -l
#SBATCH --job-name=mm_monte_carlo
#SBATCH --partition=uri-cpu,cpu
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/monte_carlo_%j.out
#SBATCH --error=logs/monte_carlo_%j.err

set -euo pipefail

export PROJECT_ROOT="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
cd "$PROJECT_ROOT"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate "/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"

echo "Node: $(hostname) | Job ID: $SLURM_JOB_ID | Monte Carlo Resampling (100k paths)"

EXPERIMENT_ID="${EXPERIMENT_ID:-EXP_MC_$(date +%Y%m%d_%H%M%S)}"
OUTPUT_DIR="$PROJECT_ROOT/outputs/$EXPERIMENT_ID"
mkdir -p "$OUTPUT_DIR"

python3 -m src.research.runners.run_monte_carlo \
    --paths 100000 \
    --output-dir "$OUTPUT_DIR" \
    --experiment-id "$EXPERIMENT_ID"
