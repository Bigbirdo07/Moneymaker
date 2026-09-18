#!/usr/bin/env bash
# Check status of Slurm jobs on UMass Amherst Unity HPC
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"

JOB_ID="${1:-}"

echo "======================================================================"
echo "UMASS AMHERST UNITY HPC: SLURM JOB STATUS"
echo "======================================================================"

if [ -z "$JOB_ID" ]; then
    echo "==> Active Moneymaker Slurm Jobs for $USER:"
    ssh "$REMOTE_HOST" "squeue --me -o '%.10i %.12P %.30j %.8u %.8T %.10M %.6D %R'"
else
    echo "==> Status for Job ID: $JOB_ID"
    ssh "$REMOTE_HOST" "squeue -j $JOB_ID 2>/dev/null || sacct -j $JOB_ID --format=JobID,JobName,Partition,State,Elapsed,ExitCode"
    
    echo ""
    echo "==> Recent Slurm Log Output (last 25 lines):"
    ssh "$REMOTE_HOST" "LOG_FILE=\$(ls -t $REMOTE_DIR/logs/slurm_*_${JOB_ID}.log 2>/dev/null | head -n1); if [ -n \"\$LOG_FILE\" ]; then echo \"Log: \$LOG_FILE\"; tail -n 25 \"\$LOG_FILE\"; else echo 'No log file generated yet.'; fi"
fi
echo "======================================================================"
