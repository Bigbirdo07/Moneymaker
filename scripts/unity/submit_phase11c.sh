#!/bin/bash
# ==============================================================================
# SUBMIT PHASE 11C FRESH REPLICATION PIPELINE TO UMASS AMHERST UNITY HPC
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="/Users/albertopaz/Moneymaker"

echo "======================================================================"
echo "SUBMITTING PHASE 11C ENGINE V3 FRESH REPLICATION HOLDOUT TO UNITY HPC"
echo "Target Cluster : UMass Amherst Unity HPC"
echo "Partition      : uri-cpu (32 CPUs, 96GB RAM)"
echo "Mode           : 2023 FRESH UNTOUCHED REAL-MARKET HOLDOUT EXAM"
echo "======================================================================"

# Step 1: Create Remote Directories
echo "==> Creating remote directories on Unity..."
ssh ${REMOTE_HOST} "mkdir -p ${REMOTE_DIR}/{src,scripts/unity,jobs,data/processed/alpaca_2021_2023_1m,logs,artifacts/unity/phase11c}"

# Step 2: Sync Codebase
echo "==> Syncing codebase..."
rsync -avz --delete \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.pytest_cache' \
    --exclude 'node_modules' \
    --exclude '/data/' \
    --exclude '/artifacts/unity/' \
    "${LOCAL_DIR}/" "${REMOTE_HOST}:${REMOTE_DIR}/"

# Step 3: Sync 2021-2023 Real Market Data
echo "==> Syncing 2021-2023 Real Alpaca/IEX Parquet Data..."
rsync -avz \
    "${LOCAL_DIR}/data/processed/alpaca_2021_2023_1m/" "${REMOTE_HOST}:${REMOTE_DIR}/data/processed/alpaca_2021_2023_1m/"

# Step 4: Submit Slurm Job
echo "==> Submitting Slurm Job to Unity Cluster..."
SUBMIT_OUTPUT=$(ssh ${REMOTE_HOST} "cd ${REMOTE_DIR} && sbatch jobs/phase11c_replication.slurm")
echo "${SUBMIT_OUTPUT}"

JOB_ID=$(echo "${SUBMIT_OUTPUT}" | grep -oE '[0-9]+')

echo ""
echo "======================================================================"
echo "JOB SUBMITTED SUCCESSFULLY: Slurm Job ID = ${JOB_ID}"
echo "======================================================================"
echo "To monitor status:"
echo "  ./scripts/unity/check_phase11c_job.sh ${JOB_ID}"
echo ""
echo "To tail the remote log in real-time:"
echo "  ssh unity \"tail -f ${REMOTE_DIR}/logs/slurm_phase11c_${JOB_ID}.log\""
echo ""
echo "After job completion, pull results back to your Mac:"
echo "  ./scripts/unity/pull_phase11c_results.sh"
echo "======================================================================"
