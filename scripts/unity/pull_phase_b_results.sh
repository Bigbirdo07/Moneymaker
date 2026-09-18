#!/bin/bash
# ==============================================================================
# PULL PHASE B ARTIFACTS AND LEDGERS FROM UNITY HPC TO LOCAL MAC
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="/Users/albertopaz/Moneymaker"

echo "======================================================================"
echo "PULLING PHASE B ARTIFACTS FROM UMASS AMHERST UNITY HPC"
echo "======================================================================"

# Pull Top-Level Parquet Ledgers and Markdown Reports
echo "==> Pulling Phase B Parquet ledgers, JSON manifests, and Markdown reports..."
rsync -avz --progress \
    --include 'DYNAMIC_*' \
    --include 'UNIVERSE_*' \
    --include 'RANKING_*' \
    --include 'SECTOR_*' \
    --include 'FAST_*' \
    --include 'PHASE_B_*' \
    --include 'daily_universe_manifest.parquet' \
    --include 'universe_exclusions.parquet' \
    --include 'liquidity_metrics.parquet' \
    --include 'universe_size_results.parquet' \
    --exclude '*' \
    "${REMOTE_HOST}:${REMOTE_DIR}/" "${LOCAL_DIR}/"

# Pull Artifact Bundles
echo "==> Pulling full experiment artifact bundles..."
rsync -avz --progress \
    "${REMOTE_HOST}:${REMOTE_DIR}/artifacts/unity/phase_b/" "${LOCAL_DIR}/artifacts/unity/phase_b/"

# Pull Slurm Logs
echo "==> Pulling Slurm execution logs..."
rsync -avz --progress \
    "${REMOTE_HOST}:${REMOTE_DIR}/logs/slurm_phase_b_*.log" "${LOCAL_DIR}/logs/" || true

echo ""
echo "======================================================================"
echo "PHASE B ARTIFACTS PULLED TO LOCAL REPOSITORY SUCCESSFULLY"
echo "======================================================================"
ls -la ${LOCAL_DIR}/PHASE_B_* ${LOCAL_DIR}/UNIVERSE_* ${LOCAL_DIR}/DYNAMIC_*
