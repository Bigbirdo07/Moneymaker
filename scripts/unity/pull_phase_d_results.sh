#!/bin/bash
# ==============================================================================
# PULL PHASE D ARTIFACTS AND PROVENANCE FROM UNITY HPC TO LOCAL REPO
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="/Users/albertopaz/Moneymaker"

echo "======================================================================"
echo "PULLING PHASE D ARTIFACTS FROM UMASS AMHERST UNITY HPC"
echo "======================================================================"

echo "==> Pulling Phase D Parquet ledgers, JSON manifests, and Markdown reports..."
rsync -avz --progress \
    --include 'RISK_*.md' \
    --include 'STOP_*.md' \
    --include 'VOLATILITY_*.md' \
    --include 'EDGE_*.md' \
    --include 'DAILY_*.md' \
    --include 'DRAWDOWN_*.md' \
    --include 'CAPITAL_*.md' \
    --include 'CAPACITY_*.md' \
    --include 'POSITION_*.md' \
    --include 'PORTFOLIO_*.md' \
    --include 'PHASE_D_*.md' \
    --include 'PHASE_D_*.json' \
    --include 'position_size_decisions.parquet' \
    --include 'capital_scale_results.parquet' \
    --include 'risk_budget_results.parquet' \
    --include 'capacity_constraints.parquet' \
    --exclude '*' \
    ${REMOTE_HOST}:${REMOTE_DIR}/ ${LOCAL_DIR}/

echo "==> Pulling full experiment artifact bundles..."
rsync -avz --progress \
    ${REMOTE_HOST}:${REMOTE_DIR}/artifacts/unity/phase_d/ \
    ${LOCAL_DIR}/artifacts/unity/phase_d/

echo "==> Pulling Slurm execution logs..."
rsync -avz --progress \
    ${REMOTE_HOST}:${REMOTE_DIR}/logs/slurm_phase_d_*.log \
    ${LOCAL_DIR}/logs/ || true

echo ""
echo "======================================================================"
echo "PHASE D ARTIFACTS PULLED TO LOCAL REPOSITORY SUCCESSFULLY"
echo "======================================================================"
ls -la ${LOCAL_DIR}/PHASE_D_*.md ${LOCAL_DIR}/PHASE_D_*.json || true
