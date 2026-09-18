#!/bin/bash
# ==============================================================================
# PULL PHASE F ARTIFACTS AND PROVENANCE FROM UNITY HPC TO LOCAL REPO
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="/Users/albertopaz/Moneymaker"

echo "======================================================================"
echo "PULLING PHASE F ARTIFACTS FROM UMASS AMHERST UNITY HPC"
echo "======================================================================"

echo "==> Pulling Phase F Parquet ledgers, JSON manifests, and Markdown reports..."
rsync -avz --progress \
    --include 'PAPER_*.md' \
    --include 'BROKER_*.md' \
    --include 'EXECUTION_*.md' \
    --include 'CAPITAL_*.md' \
    --include 'RUNTIME_*.md' \
    --include 'RECONCILIATION_*.md' \
    --include 'ORDER_*.md' \
    --include 'FAILURE_*.md' \
    --include 'EOD_*.md' \
    --include 'POST_CLOSE_*.md' \
    --include 'FORWARD_*.md' \
    --include 'PHASE_F_*.md' \
    --include 'PHASE_F_*.json' \
    --include 'PAPER_RUNTIME_FREEZE_MANIFEST.json' \
    --include 'paper_sessions.parquet' \
    --include 'paper_decisions.parquet' \
    --include 'runtime_events.parquet' \
    --include 'daily_reconciliation.parquet' \
    --include 'operational_incidents.parquet' \
    --exclude '*' \
    ${REMOTE_HOST}:${REMOTE_DIR}/ ${LOCAL_DIR}/

echo "==> Pulling full experiment artifact bundles..."
rsync -avz --progress \
    ${REMOTE_HOST}:${REMOTE_DIR}/artifacts/unity/phase_f/ \
    ${LOCAL_DIR}/artifacts/unity/phase_f/

echo "==> Pulling Slurm execution logs..."
rsync -avz --progress \
    ${REMOTE_HOST}:${REMOTE_DIR}/logs/slurm_phase_f_*.log \
    ${LOCAL_DIR}/logs/ || true

echo ""
echo "======================================================================"
echo "PHASE F ARTIFACTS PULLED TO LOCAL REPOSITORY SUCCESSFULLY"
echo "======================================================================"
ls -la ${LOCAL_DIR}/PHASE_F_*.md ${LOCAL_DIR}/PHASE_F_*.json || true
