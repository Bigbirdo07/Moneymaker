#!/bin/bash
# ==============================================================================
# CHECK PHASE E SLURM JOB STATUS ON UNITY HPC
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
JOB_ID="${1:-}"

if [[ -z "$JOB_ID" ]]; then
    echo "Usage: $0 <JOB_ID>"
    echo "Currently running jobs for user:"
    ssh ${REMOTE_HOST} "squeue -u \$USER"
    exit 0
fi

echo "======================================================================"
echo "CHECKING SLURM JOB ${JOB_ID} ON UNITY HPC"
echo "======================================================================"

ssh ${REMOTE_HOST} "
echo '==> Slurm Queue Status:'
squeue -j ${JOB_ID} || echo 'Job not in active queue.'
echo ''
echo '==> Sacct Accounting Record:'
sacct -j ${JOB_ID} --format=JobID,JobName,Partition,AllocCPUS,Elapsed,State,ExitCode || true
echo ''
echo '==> Last 30 lines of Slurm Log:'
if [ -f ${REMOTE_DIR}/logs/slurm_phase_e_${JOB_ID}.log ]; then
    tail -n 30 ${REMOTE_DIR}/logs/slurm_phase_e_${JOB_ID}.log
else
    echo 'Log file not found yet.'
fi
"
