#!/bin/bash
# ==============================================================================
# MONITOR PHASE 11A SLURM JOB STATUS ON UMASS AMHERST UNITY HPC
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
JOB_ID="${1:-}"

echo "======================================================================"
echo "UMASS AMHERST UNITY HPC: PHASE 11A SLURM JOB STATUS"
echo "======================================================================"

if [ -z "${JOB_ID}" ]; then
    echo "==> Active Phase 11A Slurm Jobs for user: $(ssh ${REMOTE_HOST} 'whoami')"
    ssh ${REMOTE_HOST} "squeue -u \$(whoami) --name=mm_phase11a -o '%.10i %.10P %.18j %.8u %.2t %.10M %.6D %R'"
else
    echo "==> Status for Job ID: ${JOB_ID}"
    ssh ${REMOTE_HOST} "squeue -j ${JOB_ID} -o '%.10i %.10P %.18j %.8u %.2t %.10M %.6D %R' || true"
    
    echo ""
    echo "==> Recent Slurm Log Output (last 25 lines):"
    echo "Log: ${REMOTE_DIR}/logs/slurm_phase11a_${JOB_ID}.log"
    echo "======================================================================"
    ssh ${REMOTE_HOST} "if [ -f '${REMOTE_DIR}/logs/slurm_phase11a_${JOB_ID}.log' ]; then tail -n 25 '${REMOTE_DIR}/logs/slurm_phase11a_${JOB_ID}.log'; else echo 'Log file not yet created.'; fi" || true
    echo "======================================================================"
fi
