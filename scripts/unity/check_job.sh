#!/usr/bin/env bash
# Query Slurm queue or tail log for a specific job on Unity
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"

if [ "$#" -eq 0 ]; then
    echo "==> Active Slurm jobs for current user on Unity:"
    ssh "$REMOTE_HOST" "squeue -u \$USER"
else
    JOB_ID="$1"
    echo "==> Status for Slurm Job ID: $JOB_ID"
    ssh "$REMOTE_HOST" "squeue -j $JOB_ID || echo 'Job $JOB_ID not active in queue.'"
    echo "==> Latest log output for job $JOB_ID (if available):"
    ssh "$REMOTE_HOST" "tail -n 25 $REMOTE_DIR/logs/*${JOB_ID}*.out 2>/dev/null || echo 'No log file found yet.'"
fi
