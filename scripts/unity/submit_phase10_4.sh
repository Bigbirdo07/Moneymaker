#!/usr/bin/env bash
# Submit Phase 10.4 Slurm Job to UMass Amherst Unity HPC
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"

MODE="full"
if [ "${1:-}" == "--smoke" ] || [ "${1:-}" == "-s" ]; then
    MODE="smoke"
fi

if [ "$MODE" == "smoke" ]; then
    SLURM_FILE="jobs/phase10_4_smoke_baseline.slurm"
    echo "==> Submitting PRE-FLIGHT BASELINE SMOKE TEST to Unity HPC..."
else
    SLURM_FILE="jobs/phase10_4_full_research.slurm"
    echo "==> Submitting FULL PHASE 10.4 RESEARCH PIPELINE to Unity HPC..."
fi

# Submit via SSH
SUBMIT_OUTPUT=$(ssh "$REMOTE_HOST" "cd $REMOTE_DIR && sbatch $SLURM_FILE")
echo "$SUBMIT_OUTPUT"

# Extract Job ID
JOB_ID=$(echo "$SUBMIT_OUTPUT" | grep -oE '[0-9]+' | tail -n1)

echo ""
echo "======================================================================"
echo "JOB SUBMITTED SUCCESSFULLY: Slurm Job ID = $JOB_ID"
echo "======================================================================"
echo "To monitor status:"
echo "  ./scripts/unity/check_phase10_4_job.sh $JOB_ID"
echo ""
echo "To tail the remote log in real-time:"
echo "  ssh $REMOTE_HOST \"tail -f $REMOTE_DIR/logs/slurm_*_${JOB_ID}.log\""
echo ""
echo "After job completion, pull results back to your Mac:"
echo "  ./scripts/unity/pull_phase10_4_results.sh"
echo "======================================================================"
