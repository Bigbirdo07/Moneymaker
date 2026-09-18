#!/usr/bin/env bash
# Submit Phase 10.5 Single-Pass Final Real Holdout Exam to UMass Amherst Unity HPC

set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"

echo "======================================================================"
echo "SUBMITTING PHASE 10.5 SINGLE-PASS FINAL REAL HOLDOUT EXAM (AUGUST 2026)"
echo "Target Cluster : UMass Amherst Unity HPC"
echo "Partition      : uri-cpu (32 CPUs, 96GB RAM)"
echo "Mode           : SINGLE-PASS FINAL HISTORICAL EXAM"
echo "======================================================================"

# Sync codebase to Unity first
./scripts/unity/sync_phase10_4_to_unity.sh

echo ""
echo "==> Submitting Slurm Job to Unity Cluster..."
SUBMIT_OUTPUT=$(ssh "$REMOTE_HOST" "cd '$REMOTE_DIR' && sbatch jobs/phase10_5_final_holdout.slurm")
echo "$SUBMIT_OUTPUT"

JOB_ID=$(echo "$SUBMIT_OUTPUT" | grep -oE '[0-9]+' | tail -n 1)

echo ""
echo "======================================================================"
echo "JOB SUBMITTED SUCCESSFULLY: Slurm Job ID = $JOB_ID"
echo "======================================================================"
echo "To monitor status:"
echo "  ./scripts/unity/check_phase10_5_job.sh $JOB_ID"
echo ""
echo "To tail the remote log in real-time:"
echo "  ssh unity \"tail -f /scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/logs/slurm_phase10_5_${JOB_ID}.log\""
echo ""
echo "After job completion, pull results back to your Mac:"
echo "  ./scripts/unity/pull_phase10_5_results.sh"
echo "======================================================================"
