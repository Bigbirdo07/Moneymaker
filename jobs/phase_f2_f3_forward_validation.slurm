#!/bin/bash
#SBATCH --job-name=mm_phase_f2_f3
#SBATCH --partition=uri-cpu,cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/logs/slurm_phase_f2_f3_%j.log
#SBATCH --error=/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/logs/slurm_phase_f2_f3_%j.err

set -euo pipefail

TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
EXPERIMENT_ID="PHASE_F2_F3_FORWARD_${TIMESTAMP}"
WORK_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
ARTIFACT_DIR="${WORK_DIR}/artifacts/unity/phase_f2_f3/${EXPERIMENT_ID}"
LOG_DIR="${WORK_DIR}/logs"

mkdir -p "${ARTIFACT_DIR}" "${LOG_DIR}"

echo "======================================================================"
echo "SLURM JOB: Phase F2 / F3 Forward Operational Validation"
echo "Job ID        : ${SLURM_JOB_ID:-LOCAL}"
echo "Experiment ID : ${EXPERIMENT_ID}"
echo "Node          : $(hostname)"
echo "CPUs / Mem    : 16 CPUs / 64GB RAM"
echo "Start Time    : $(date -u)"
echo "======================================================================"

CONDA_ENV_PATH="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"
PYTHON_BIN="${CONDA_ENV_PATH}/bin/python"

echo "==> Activating Conda Environment: ${CONDA_ENV_PATH}"
echo "==> Python Interpreter: ${PYTHON_BIN}"
${PYTHON_BIN} -c "import sys, sklearn, pandas, numpy, yaml; print('Environment OK:', sys.version)"

cd "${WORK_DIR}"
export PYTHONPATH="${WORK_DIR}:${PYTHONPATH:-}"

echo ""
echo "==> Launching Phase F2 / F3 Forward Operational Validation Pipeline..."
${PYTHON_BIN} scripts/run_phase_f2_f3_forward_validation.py \
    --data-dir data/processed/alpaca_extended_1m \
    --session-date 2026-07-31 \
    --output-dir "${ARTIFACT_DIR}"

echo ""
echo "==> Copying artifacts to top-level working directory for immediate sync..."
cp -f "${ARTIFACT_DIR}"/*.md "${WORK_DIR}/" || true
cp -f "${ARTIFACT_DIR}"/*.parquet "${WORK_DIR}/" || true
cp -f "${ARTIFACT_DIR}"/*.json "${WORK_DIR}/" || true

echo "{\"experiment_id\": \"${EXPERIMENT_ID}\", \"slurm_job_id\": \"${SLURM_JOB_ID:-LOCAL}\", \"node\": \"$(hostname)\", \"timestamp\": \"${TIMESTAMP}\"}" > "${ARTIFACT_DIR}/experiment_manifest.json"

echo ""
echo "======================================================================"
echo "PHASE F2 / F3 FORWARD OPERATIONAL VALIDATION COMPLETED: $(date -u)"
echo "Artifact Bundle Ready at: ${ARTIFACT_DIR}"
echo "======================================================================"
