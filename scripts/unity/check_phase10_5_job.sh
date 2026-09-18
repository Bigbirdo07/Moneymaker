#!/usr/bin/env bash
# Check Phase 10.5 Slurm Job Status and tail remote log

set -euo pipefail

JOB_ID="${1:-}"
REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"

echo "======================================================================"
echo "UMASS AMHERST UNITY HPC: PHASE 10.5 SLURM JOB STATUS"
echo "======================================================================"

if [ -n "$JOB_ID" ]; then
    echo "==> Status for Job ID: $JOB_ID"
    ssh "$REMOTE_HOST" "squeue -j '$JOB_ID' 2>/dev/null || sacct -j '$JOB_ID' --format=JobID,JobName,Partition,AllocCPUS,State,ExitCode,Elapsed"
    
    echo ""
    echo "==> Recent Slurm Log Output (last 25 lines):"
    ssh "$REMOTE_HOST" "
        LOG_FILE=\$(ls -t '$REMOTE_DIR'/logs/slurm_phase10_5_${JOB_ID}.log 2>/dev/null | head -n 1)
        if [ -n \"\$LOG_FILE\" ] && [ -f \"\$LOG_FILE\" ]; then
            echo \"Log: \$LOG_FILE\"
            tail -n 25 \"\$LOG_FILE\"
        else
            echo \"No log file found yet for job $JOB_ID.\"
        fi
    "
else
    echo "==> Active Phase 10.5 jobs for user:"
    ssh "$REMOTE_HOST" "squeue -u \$USER --format=\"%.18i %.9P %.20j %.8u %.2t %.10M %.6D %R\""
fi
echo "======================================================================"
