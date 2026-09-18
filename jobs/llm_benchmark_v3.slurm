#!/bin/bash -l
#SBATCH --job-name=mm_llm_benchmark_v3
#SBATCH --partition=uri-gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/llm_benchmark_v3_%j.out
#SBATCH --error=logs/llm_benchmark_v3_%j.err

set -euo pipefail

export PROJECT_ROOT="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
export HF_HOME="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface"
cd "$PROJECT_ROOT"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate "/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"

export PATH="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice/bin:$PATH"
export PYTHON_BIN="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice/bin/python3"

export QWEN_MODEL_PATH="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8"

echo "Node: $(hostname) | Job ID: $SLURM_JOB_ID | Base Model: Qwen 2.5 14B Instruct"
echo "Python: $("$PYTHON_BIN" --version) at $PYTHON_BIN"

OUTPUT_DIR="$PROJECT_ROOT/outputs/evaluations"
mkdir -p "$OUTPUT_DIR"

MMRM_02_ADAPTER="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/outputs/EXP_MMRM_0_2_REAL_20260916_190643/adapter"

echo "=== 1. Evaluating MMRM-0.2-REAL (No RAG) ==="
"$PYTHON_BIN" -m src.research.runners.run_benchmark_v3 \
    --base-model-path "$QWEN_MODEL_PATH" \
    --adapter-path "$MMRM_02_ADAPTER" \
    --output-dir "$OUTPUT_DIR" \
    --condition "MMRM_0_2_ONLY"

echo "=== 2. Evaluating MMRM-0.2-REAL + RAG ==="
"$PYTHON_BIN" -m src.research.runners.run_benchmark_v3 \
    --base-model-path "$QWEN_MODEL_PATH" \
    --adapter-path "$MMRM_02_ADAPTER" \
    --output-dir "$OUTPUT_DIR" \
    --condition "MMRM_0_2_RAG" \
    --use-rag

echo "=== Real Benchmark V3 Inference Complete ==="
