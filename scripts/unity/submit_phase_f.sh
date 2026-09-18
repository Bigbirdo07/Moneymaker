#!/bin/bash
# ==============================================================================
# SUBMIT PHASE F PAPER RUNTIME RESEARCH JOB TO UNITY HPC
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"

echo "======================================================================"
echo "SYNCHRONIZING PHASE F CODEBASE TO UNITY HPC"
echo "======================================================================"

rsync -avz --exclude '.git' \
    --exclude '.venv' \
    --exclude 'node_modules' \
    --exclude 'workstation/node_modules' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.pytest_cache' \
    --exclude 'data/raw' \
    --exclude 'artifacts/unity' \
    ./ ${REMOTE_HOST}:${REMOTE_DIR}/

echo "==> Submitting Phase F Slurm Job on Unity..."
SUBMIT_OUT=$(ssh ${REMOTE_HOST} "cd ${REMOTE_DIR} && sbatch jobs/phase_f_paper_runtime.slurm")
echo "${SUBMIT_OUT}"

JOB_ID=$(echo "${SUBMIT_OUT}" | awk '{print $4}')
echo "Job ID: ${JOB_ID}"
echo "Use './scripts/unity/check_phase_f_job.sh ${JOB_ID}' to monitor progress."
