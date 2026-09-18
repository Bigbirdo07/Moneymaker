#!/bin/bash
set -euo pipefail

REMOTE_HOST="unity"
JOB_ID="${1:-64562208}"

echo "======================================================================"
echo "CHECKING UNITY HPC JOB STATUS: ${JOB_ID}"
echo "======================================================================"
ssh ${REMOTE_HOST} "squeue -j ${JOB_ID} || true"
echo ""
echo "==> Job Accounting (sacct):"
ssh ${REMOTE_HOST} "sacct -j ${JOB_ID} --format=JobID,JobName,Partition,State,Elapsed,ExitCode || true"
echo ""
echo "==> Recent Slurm Logs:"
ssh ${REMOTE_HOST} "tail -n 25 /scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/logs/slurm_phase_f2_f3_${JOB_ID}.log 2>/dev/null || true"
