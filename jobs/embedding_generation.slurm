#!/bin/bash -l
#SBATCH --job-name=mm_embeddings
#SBATCH --partition=uri-gpu,uri-cpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/embeddings_%j.out
#SBATCH --error=logs/embeddings_%j.err

set -euo pipefail

export PROJECT_ROOT="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
cd "$PROJECT_ROOT"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate "/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"

echo "Node: $(hostname) | Job ID: $SLURM_JOB_ID | Embedding Corpus Refresh"

python3 -m src.research.runners.run_embedding_generation \
    --corpus-dir "$PROJECT_ROOT/research_corpus" \
    --output-index "$PROJECT_ROOT/embeddings/research_index.faiss"
