#!/bin/bash -l
#SBATCH --job-name=mm_gpu_training
#SBATCH --partition=uri-gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=06:00:00
#SBATCH --output=logs/gpu_train_%j.out
#SBATCH --error=logs/gpu_train_%j.err

set -euo pipefail

export PROJECT_ROOT="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
cd "$PROJECT_ROOT"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate "/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"

echo "Node: $(hostname) | Job ID: $SLURM_JOB_ID | GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'GPU allocated')"

EXPERIMENT_ID="${EXPERIMENT_ID:-EXP_GPU_$(date +%Y%m%d_%H%M%S)}"
CONFIG_PATH="${CONFIG_PATH:-configs/research_alpha_gpu.yaml}"
OUTPUT_DIR="$PROJECT_ROOT/outputs/$EXPERIMENT_ID"
mkdir -p "$OUTPUT_DIR"

python3 -m src.research.runners.run_gpu_training \
    --config "$CONFIG_PATH" \
    --experiment-id "$EXPERIMENT_ID" \
    --output-dir "$OUTPUT_DIR"
