#!/bin/bash
# ==============================================================================
# PULL PHASE C ARTIFACTS AND PROVENANCE FROM UNITY HPC TO LOCAL REPO
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="/Users/albertopaz/Moneymaker"

echo "======================================================================"
echo "PULLING PHASE C ARTIFACTS FROM UMASS AMHERST UNITY HPC"
echo "======================================================================"

echo "==> Pulling Phase C Parquet ledgers, JSON manifests, and Markdown reports..."
rsync -avz --progress \
    --include 'EVENT_*.md' \
    --include 'PHASE_C_*.md' \
    --include 'PHASE_C_*.json' \
    --include 'event_*.parquet' \
    --exclude '*' \
    ${REMOTE_HOST}:${REMOTE_DIR}/ ${LOCAL_DIR}/

echo "==> Pulling full experiment artifact bundles..."
rsync -avz --progress \
    ${REMOTE_HOST}:${REMOTE_DIR}/artifacts/unity/phase_c/ \
    ${LOCAL_DIR}/artifacts/unity/phase_c/

echo "==> Pulling Slurm execution logs..."
rsync -avz --progress \
    ${REMOTE_HOST}:${REMOTE_DIR}/logs/slurm_phase_c_*.log \
    ${LOCAL_DIR}/logs/ || true

echo ""
echo "======================================================================"
echo "PHASE C ARTIFACTS PULLED TO LOCAL REPOSITORY SUCCESSFULLY"
echo "======================================================================"
ls -la ${LOCAL_DIR}/EVENT_*.md ${LOCAL_DIR}/PHASE_C_*.md ${LOCAL_DIR}/PHASE_C_*.json || true
