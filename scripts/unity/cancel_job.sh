#!/usr/bin/env bash
# Cancel a running or queued job on Unity
set -euo pipefail

REMOTE_HOST="unity"

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <job_id>"
    exit 1
fi

JOB_ID="$1"
echo "==> Cancelling Slurm Job $JOB_ID on Unity..."
ssh "$REMOTE_HOST" "scancel $JOB_ID"
echo "==> Cancel command issued."
