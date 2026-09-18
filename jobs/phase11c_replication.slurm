#!/bin/bash
#SBATCH --job-name=mm_phase11c
#SBATCH --partition=uri-cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=96G
#SBATCH --time=02:00:00
#SBATCH --output=/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/logs/slurm_phase11c_%j.log
#SBATCH --error=/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/logs/slurm_phase11c_%j.err

set -euo pipefail

TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
EXPERIMENT_ID="PHASE11C_V3_${TIMESTAMP}"
WORK_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
ARTIFACT_DIR="${WORK_DIR}/artifacts/unity/phase11c/${EXPERIMENT_ID}"
LOG_DIR="${WORK_DIR}/logs"

mkdir -p "${ARTIFACT_DIR}" "${LOG_DIR}"

echo "======================================================================"
echo "SLURM JOB: Phase 11C Engine V3 Fresh Historical Replication Holdout"
echo "Job ID        : ${SLURM_JOB_ID:-LOCAL}"
echo "Experiment ID : ${EXPERIMENT_ID}"
echo "Node          : $(hostname)"
echo "CPUs / Mem    : 32 CPUs / 96GB RAM"
echo "Start Time    : $(date -u)"
echo "======================================================================"

CONDA_ENV_PATH="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"
PYTHON_BIN="${CONDA_ENV_PATH}/bin/python"

echo "==> Activating Conda Environment: ${CONDA_ENV_PATH}"
echo "==> Python Interpreter: ${PYTHON_BIN}"
${PYTHON_BIN} -c "import sys, sklearn, pandas, numpy; print('Environment OK:', sys.version)"

cd "${WORK_DIR}"
export PYTHONPATH="${WORK_DIR}:${PYTHONPATH:-}"

echo ""
echo "==> Launching Phase 11C Fresh Replication Pipeline on Unity HPC..."
${PYTHON_BIN} scripts/run_phase11c_replication.py \
    --data-dir data/processed/alpaca_2021_2023_1m \
    --output-dir "${ARTIFACT_DIR}"

echo ""
echo "==> Copying artifacts to top-level working directory for immediate sync..."
cp -f "${ARTIFACT_DIR}"/PHASE_11C_* "${WORK_DIR}/" || true
cp -f "${ARTIFACT_DIR}"/ENGINE_V3_* "${WORK_DIR}/" || true

echo "{\"experiment_id\": \"${EXPERIMENT_ID}\", \"slurm_job_id\": \"${SLURM_JOB_ID:-LOCAL}\", \"node\": \"$(hostname)\", \"timestamp\": \"${TIMESTAMP}\"}" > "${ARTIFACT_DIR}/experiment_manifest.json"

echo ""
echo "======================================================================"
echo "PHASE 11C FRESH REPLICATION COMPLETED: $(date -u)"
echo "Artifact Bundle Ready at: ${ARTIFACT_DIR}"
echo "======================================================================"
