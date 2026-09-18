#!/bin/bash
# ==============================================================================
# SUBMIT PHASE 11A BROADER REAL-MARKET REGIME VALIDATION TO UMASS AMHERST UNITY HPC
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="/Users/albertopaz/Moneymaker"

echo "======================================================================"
echo "SUBMITTING PHASE 11A BROADER REGIME VALIDATION (2025 WALK-FORWARD)"
echo "Target Cluster : UMass Amherst Unity HPC"
echo "Partition      : uri-cpu (32 CPUs, 96GB RAM)"
echo "Mode           : 12-MONTH ROLLING WALK-FORWARD REGIME VALIDATION"
echo "======================================================================"

# Step 1: Sync Codebase and Manifests
"${LOCAL_DIR}/scripts/unity/sync_phase10_4_to_unity.sh"

# Step 2: Submit Slurm Job
echo "==> Submitting Slurm Job to Unity Cluster..."
SUBMIT_OUTPUT=$(ssh ${REMOTE_HOST} "cd ${REMOTE_DIR} && sbatch jobs/phase11a_regime_validation.slurm")
echo "${SUBMIT_OUTPUT}"

JOB_ID=$(echo "${SUBMIT_OUTPUT}" | grep -oE '[0-9]+')

echo ""
echo "======================================================================"
echo "JOB SUBMITTED SUCCESSFULLY: Slurm Job ID = ${JOB_ID}"
echo "======================================================================"
echo "To monitor status:"
echo "  ./scripts/unity/check_phase11a_job.sh ${JOB_ID}"
echo ""
echo "To tail the remote log in real-time:"
echo "  ssh unity \"tail -f ${REMOTE_DIR}/logs/slurm_phase11a_${JOB_ID}.log\""
echo ""
echo "After job completion, pull results back to your Mac:"
echo "  ./scripts/unity/pull_phase11a_results.sh"
echo "======================================================================"
