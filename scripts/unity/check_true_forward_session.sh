#!/bin/bash
# ==============================================================================
# MONITOR TRUE FORWARD PAPER SESSION ON UNITY HPC
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
JOB_ID="${1:-}"

if [ -z "${JOB_ID}" ]; then
    echo "Usage: $0 <JOB_ID>"
    echo "Active slurm jobs:"
    ssh ${REMOTE_HOST} "squeue -u \$USER"
    exit 1
fi

echo "======================================================================"
echo "CHECKING SLURM JOB: ${JOB_ID}"
echo "======================================================================"

ssh ${REMOTE_HOST} "squeue -j ${JOB_ID}" || true

echo ""
echo "==> Recent Slurm Out Log:"
ssh ${REMOTE_HOST} "tail -n 40 ${REMOTE_DIR}/logs/slurm_true_forward_${JOB_ID}.log" 2>/dev/null || echo "Log not ready yet."

echo ""
echo "==> Recent Slurm Err Log:"
ssh ${REMOTE_HOST} "tail -n 20 ${REMOTE_DIR}/logs/slurm_true_forward_${JOB_ID}.err" 2>/dev/null || echo "Err log empty."
