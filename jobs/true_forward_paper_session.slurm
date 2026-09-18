#!/bin/bash
#SBATCH --job-name=mm_true_forward
#SBATCH --partition=uri-cpu,cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --output=/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/logs/slurm_true_forward_%j.log
#SBATCH --error=/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/logs/slurm_true_forward_%j.err

set -euo pipefail

TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
WORK_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOG_DIR="${WORK_DIR}/logs"
ARTIFACT_DIR="${WORK_DIR}/artifacts/forward"

mkdir -p "${LOG_DIR}" "${ARTIFACT_DIR}"

echo "======================================================================"
echo "SLURM JOB: Moneymaker True Forward Paper Session (Session 1 / 20)"
echo "Job ID        : ${SLURM_JOB_ID:-LOCAL}"
echo "Node          : $(hostname)"
echo "CPUs / Mem    : 8 CPUs / 32GB RAM"
echo "Start Time    : $(date -u)"
echo "======================================================================"

CONDA_ENV_PATH="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"
PYTHON_BIN="${CONDA_ENV_PATH}/bin/python"

echo "==> Activating Python Environment: ${CONDA_ENV_PATH}"
${PYTHON_BIN} -c "import sys, sklearn, pandas, numpy, yaml; print('Python Environment OK:', sys.version)"

cd "${WORK_DIR}"
export PYTHONPATH="${WORK_DIR}:${PYTHONPATH:-}"

# Load credentials from .env if present
if [ -f "${WORK_DIR}/.env" ]; then
    set -a
    source "${WORK_DIR}/.env"
    set +a
fi

SESSION_DATE="${1:-2026-09-21}"

echo ""
echo "==> Launching True Forward Paper Session for Market Date: ${SESSION_DATE}..."
${PYTHON_BIN} scripts/run_true_forward_paper_session.py \
    --session-date "${SESSION_DATE}" \
    --output-dir "${ARTIFACT_DIR}"

echo ""
echo "======================================================================"
echo "TRUE FORWARD PAPER SESSION PIPELINE COMPLETED: $(date -u)"
echo "======================================================================"
