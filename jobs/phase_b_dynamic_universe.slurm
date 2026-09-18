#!/bin/bash
#SBATCH --job-name=mm_phase_b
#SBATCH --partition=uri-cpu,cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=96G
#SBATCH --time=02:00:00
#SBATCH --output=/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/logs/slurm_phase_b_%j.log
#SBATCH --error=/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/logs/slurm_phase_b_%j.err

set -euo pipefail

TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
EXPERIMENT_ID="PHASE_B_DYNAMIC_${TIMESTAMP}"
WORK_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
ARTIFACT_DIR="${WORK_DIR}/artifacts/unity/phase_b/${EXPERIMENT_ID}"
LOG_DIR="${WORK_DIR}/logs"

mkdir -p "${ARTIFACT_DIR}" "${LOG_DIR}"

echo "======================================================================"
echo "SLURM JOB: Phase B Dynamic Universe Research & Liquidity Filtering"
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
${PYTHON_BIN} -c "import sys, sklearn, pandas, numpy, scipy; print('Environment OK:', sys.version)"

cd "${WORK_DIR}"
export PYTHONPATH="${WORK_DIR}:${PYTHONPATH:-}"

echo ""
echo "==> Launching Phase B Dynamic Universe Pipeline on Unity HPC..."
${PYTHON_BIN} scripts/run_phase_b_research.py \
    --data-dir data/processed/alpaca_extended_1m \
    --output-dir "${ARTIFACT_DIR}"

echo ""
echo "==> Copying artifacts to top-level working directory for immediate sync..."
cp -f "${ARTIFACT_DIR}"/*.md "${WORK_DIR}/" || true
cp -f "${ARTIFACT_DIR}"/*.parquet "${WORK_DIR}/" || true
cp -f "${ARTIFACT_DIR}"/*.json "${WORK_DIR}/" || true

echo "{\"experiment_id\": \"${EXPERIMENT_ID}\", \"slurm_job_id\": \"${SLURM_JOB_ID:-LOCAL}\", \"node\": \"$(hostname)\", \"timestamp\": \"${TIMESTAMP}\"}" > "${ARTIFACT_DIR}/experiment_manifest.json"

echo ""
echo "======================================================================"
echo "PHASE B DYNAMIC UNIVERSE RESEARCH COMPLETED: $(date -u)"
echo "Artifact Bundle Ready at: ${ARTIFACT_DIR}"
echo "======================================================================"
