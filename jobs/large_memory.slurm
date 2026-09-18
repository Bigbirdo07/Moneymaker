#!/bin/bash -l
#SBATCH --job-name=mm_highmem
#SBATCH --partition=highmem,uri-cpu,cpu
#SBATCH --cpus-per-task=32
#SBATCH --mem=256G
#SBATCH --time=12:00:00
#SBATCH --output=logs/highmem_%j.out
#SBATCH --error=logs/highmem_%j.err

set -euo pipefail

export PROJECT_ROOT="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
cd "$PROJECT_ROOT"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate "/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"

echo "Node: $(hostname) | Job ID: $SLURM_JOB_ID | Memory: 256GB"

EXPERIMENT_ID="${EXPERIMENT_ID:-EXP_HIGHMEM_$(date +%Y%m%d_%H%M%S)}"
CONFIG_PATH="${CONFIG_PATH:-configs/research_highmem.yaml}"
OUTPUT_DIR="$PROJECT_ROOT/outputs/$EXPERIMENT_ID"
mkdir -p "$OUTPUT_DIR"

python3 -m src.research.runners.run_highmem_matrix \
    --config "$CONFIG_PATH" \
    --experiment-id "$EXPERIMENT_ID" \
    --output-dir "$OUTPUT_DIR"
