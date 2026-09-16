#!/usr/bin/env bash
# Submit a Slurm job to UMass Amherst Unity cluster
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <slurm_script_name> [extra_sbatch_args...]"
    echo "Example: $0 jobs/gpu_training.slurm"
    exit 1
fi

SLURM_SCRIPT="$1"
shift

echo "==> Submitting $SLURM_SCRIPT to Unity ($REMOTE_HOST)..."
ssh "$REMOTE_HOST" "cd $REMOTE_DIR && sbatch $* $SLURM_SCRIPT"
