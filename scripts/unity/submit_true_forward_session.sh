
#!/bin/bash
# ==============================================================================
# SUBMIT TRUE FORWARD PAPER SESSION TO UNITY HPC
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
SESSION_DATE="${1:-2026-09-21}"

echo "======================================================================"
echo "SYNCHRONIZING CODEBASE TO UNITY HPC FOR TRUE FORWARD SESSION"
echo "Target Session Date: ${SESSION_DATE}"
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

echo "==> Submitting True Forward Slurm Job on Unity..."
SUBMIT_OUT=$(ssh ${REMOTE_HOST} "cd ${REMOTE_DIR} && sbatch jobs/true_forward_paper_session.slurm ${SESSION_DATE}")
echo "${SUBMIT_OUT}"

JOB_ID=$(echo "${SUBMIT_OUT}" | awk '{print $4}')
echo "Job ID: ${JOB_ID}"
echo "Use './scripts/unity/check_true_forward_session.sh ${JOB_ID}' to monitor progress."
echo "Use './scripts/unity/pull_true_forward_session.sh' to retrieve session artifacts after completion."
