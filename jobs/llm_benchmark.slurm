#!/bin/bash -l
#SBATCH --job-name=mm_llm_benchmark
#SBATCH --partition=uri-gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/llm_benchmark_%j.out
#SBATCH --error=logs/llm_benchmark_%j.err

set -euo pipefail

export PROJECT_ROOT="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
export HF_HOME="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface"
cd "$PROJECT_ROOT"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate "/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"

export QWEN_MODEL_PATH="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8"

echo "Node: $(hostname) | Job ID: $SLURM_JOB_ID | Base Model: Qwen 2.5 14B Instruct"

ADAPTER_PATH="${ADAPTER_PATH:-}"
CONDITION="${CONDITION:-BASE_ONLY}"
OUTPUT_DIR="$PROJECT_ROOT/outputs/evaluations"
mkdir -p "$OUTPUT_DIR"

python3 -m src.research.runners.run_real_benchmark \
    --base-model-path "$QWEN_MODEL_PATH" \
    --adapter-path "$ADAPTER_PATH" \
    --output-dir "$OUTPUT_DIR" \
    --condition "$CONDITION"
