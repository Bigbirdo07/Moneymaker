#!/bin/bash
# ==============================================================================
# PULL PHASE 11C ARTIFACTS AND LEDGERS FROM UNITY HPC TO LOCAL MAC
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="/Users/albertopaz/Moneymaker"

echo "======================================================================"
echo "PULLING PHASE 11C ARTIFACTS FROM UMASS AMHERST UNITY HPC"
echo "======================================================================"

# Pull Top-Level Parquet Ledgers and Markdown Reports
echo "==> Pulling Phase 11C Parquet ledgers, JSON manifests, and Markdown reports..."
rsync -avz --progress \
    --include 'PHASE_11C_*' \
    --include 'ENGINE_V3_*' \
    --exclude '*' \
    "${REMOTE_HOST}:${REMOTE_DIR}/" "${LOCAL_DIR}/"

# Pull Artifact Bundles
echo "==> Pulling full experiment artifact bundles..."
rsync -avz --progress \
    "${REMOTE_HOST}:${REMOTE_DIR}/artifacts/unity/phase11c/" "${LOCAL_DIR}/artifacts/unity/phase11c/"

# Pull Slurm Logs
echo "==> Pulling Slurm execution logs..."
rsync -avz --progress \
    "${REMOTE_HOST}:${REMOTE_DIR}/logs/slurm_phase11c_*.log" "${LOCAL_DIR}/logs/" || true

echo ""
echo "======================================================================"
echo "PHASE 11C ARTIFACTS PULLED TO LOCAL REPOSITORY SUCCESSFULLY"
echo "======================================================================"
ls -la ${LOCAL_DIR}/PHASE_11C_* ${LOCAL_DIR}/ENGINE_V3_*
