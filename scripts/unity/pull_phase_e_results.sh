#!/bin/bash
# ==============================================================================
# PULL PHASE E ARTIFACTS AND PROVENANCE FROM UNITY HPC TO LOCAL REPO
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="/Users/albertopaz/Moneymaker"

echo "======================================================================"
echo "PULLING PHASE E ARTIFACTS FROM UMASS AMHERST UNITY HPC"
echo "======================================================================"

echo "==> Pulling Phase E Parquet ledgers, JSON manifests, and Markdown reports..."
rsync -avz --progress \
    --include 'MORNING_*.md' \
    --include 'MARKET_*.md' \
    --include 'SESSION_*.md' \
    --include 'CROSS_*.md' \
    --include 'SECTOR_*.md' \
    --include 'MACRO_*.md' \
    --include 'PREMARKET_*.md' \
    --include 'PHASE_E_*.md' \
    --include 'PHASE_E_*.json' \
    --include 'morning_briefs.parquet' \
    --include 'morning_candidate_sets.parquet' \
    --include 'session_gate_results.parquet' \
    --include 'sector_state_results.parquet' \
    --include 'macro_event_ledger.parquet' \
    --exclude '*' \
    ${REMOTE_HOST}:${REMOTE_DIR}/ ${LOCAL_DIR}/

echo "==> Pulling full experiment artifact bundles..."
rsync -avz --progress \
    ${REMOTE_HOST}:${REMOTE_DIR}/artifacts/unity/phase_e/ \
    ${LOCAL_DIR}/artifacts/unity/phase_e/

echo "==> Pulling Slurm execution logs..."
rsync -avz --progress \
    ${REMOTE_HOST}:${REMOTE_DIR}/logs/slurm_phase_e_*.log \
    ${LOCAL_DIR}/logs/ || true

echo ""
echo "======================================================================"
echo "PHASE E ARTIFACTS PULLED TO LOCAL REPOSITORY SUCCESSFULLY"
echo "======================================================================"
ls -la ${LOCAL_DIR}/PHASE_E_*.md ${LOCAL_DIR}/PHASE_E_*.json || true
