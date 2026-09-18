#!/usr/bin/env bash
#SBATCH --job-name=mm_baseline_smoke
#SBATCH --partition=uri-cpu
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=logs/slurm_baseline_smoke_%j.log
#SBATCH --error=logs/slurm_baseline_smoke_%j.err

set -euo pipefail

echo "======================================================================"
echo "SLURM JOB: Phase 10.4 Remote Baseline Smoke Test"
echo "Job ID    : ${SLURM_JOB_ID:-LOCAL}"
echo "Node      : ${SLURMD_NODENAME:-LOCAL}"
echo "Start Time: $(date)"
echo "======================================================================"

CONDA_ENV_PATH="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"
REMOTE_PROJECT_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"

cd "$REMOTE_PROJECT_DIR"
mkdir -p logs data/processed/matrix_cache artifacts/unity/phase10_4

# Activate Conda Environment
echo "==> Activating Conda Environment: $CONDA_ENV_PATH"
source /opt/anaconda3/etc/profile.d/conda.sh 2>/dev/null || source /modules/apps/miniconda/etc/profile.d/conda.sh 2>/dev/null || true
export PATH="$CONDA_ENV_PATH/bin:$PATH"
export PYTHONPATH="$REMOTE_PROJECT_DIR"

echo "==> Python Interpreter: $(which python)"
python -c "import sys, sklearn, pandas, numpy, scipy; print('Environment OK:', sys.version)"

# 1. Remote Data Verification
echo ""
echo "==> Step 1: Remote Data & Firewall Verification..."
python -u scripts/verify_remote_data.py

# 2. Baseline Model Smoke Test
echo ""
echo "==> Step 2: Running Baseline Smoke Test & Metric Match..."
python -u scripts/run_remote_baseline_smoke.py

echo ""
echo "======================================================================"
echo "SLURM BASELINE SMOKE TEST COMPLETED: $(date)"
echo "======================================================================"
