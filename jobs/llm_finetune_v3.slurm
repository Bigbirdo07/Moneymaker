#!/bin/bash -l
#SBATCH --job-name=mm_llm_finetune_v3
#SBATCH --partition=uri-gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=logs/llm_finetune_v3_%j.out
#SBATCH --error=logs/llm_finetune_v3_%j.err

set -euo pipefail

export PROJECT_ROOT="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
export HF_HOME="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface"
cd "$PROJECT_ROOT"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate "/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"

export PATH="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice/bin:$PATH"
export PYTHON_BIN="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice/bin/python3"

export QWEN_MODEL_PATH="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8"

echo "Node: $(hostname) | Job ID: $SLURM_JOB_ID | Base Model: Qwen 2.5 14B Instruct (MMRM-0.2 V3)"
echo "Python: $("$PYTHON_BIN" --version) at $PYTHON_BIN"

EXPERIMENT_ID="${EXPERIMENT_ID:-EXP_MMRM_0_2_REAL_$(date +%Y%m%d_%H%M%S)}"
DATASET_PATH="${DATASET_PATH:-data/moneymaker_llm/v3/train.jsonl}"
VAL_DATASET_PATH="${VAL_DATASET_PATH:-data/moneymaker_llm/v3/val.jsonl}"
OUTPUT_DIR="$PROJECT_ROOT/outputs/$EXPERIMENT_ID"
mkdir -p "$OUTPUT_DIR"

"$PYTHON_BIN" -m src.research.runners.run_qlora_finetune \
    --base-model-path "$QWEN_MODEL_PATH" \
    --dataset-path "$DATASET_PATH" \
    --val-dataset-path "$VAL_DATASET_PATH" \
    --output-dir "$OUTPUT_DIR" \
    --experiment-id "$EXPERIMENT_ID" \
    --lora-r 16 \
    --lora-alpha 32 \
    --learning-rate 1.5e-4 \
    --epochs 3
