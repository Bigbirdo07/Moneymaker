#!/usr/bin/env bash
# Synchronize Moneymaker code and real historical market data to UMass Amherst Unity cluster
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "======================================================================"
echo "SYNCHRONIZING MONEYMAKER TO UMASS AMHERST UNITY HPC"
echo "Remote Host : $REMOTE_HOST"
echo "Remote Dir  : $REMOTE_DIR"
echo "Local Dir   : $LOCAL_DIR"
echo "======================================================================"

# 1. Ensure remote directories exist
echo "==> [1/3] Creating directory tree on Unity..."
ssh "$REMOTE_HOST" "mkdir -p $REMOTE_DIR/{src,scripts,data/processed/alpaca_1m,data/processed/alpaca_extended_1m,data/processed/matrix_cache,logs,artifacts/unity/phase10_4,checkpoints,jobs,configs,tests}"

# 2. Sync codebase
echo "==> [2/3] Syncing codebase (src, scripts, configs, tests, jobs)..."
rsync -avz --delete \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.pytest_cache' \
    --exclude 'node_modules' \
    --exclude '/data/' \
    --exclude '/artifacts/unity/' \
    "$LOCAL_DIR/" "${REMOTE_HOST}:${REMOTE_DIR}/"

# 3. Sync real Alpaca historical data
echo "==> [3/3] Syncing real Alpaca 1-minute historical datasets (2024-2026)..."
rsync -avz \
    "$LOCAL_DIR/data/processed/alpaca_1m/" "${REMOTE_HOST}:${REMOTE_DIR}/data/processed/alpaca_1m/"

rsync -avz \
    "$LOCAL_DIR/data/processed/alpaca_extended_1m/" "${REMOTE_HOST}:${REMOTE_DIR}/data/processed/alpaca_extended_1m/"

echo ""
echo "==> Code and real market datasets synchronized to Unity successfully."
echo "==> Next: Run ./scripts/unity/submit_phase10_4.sh --smoke  (for pre-flight baseline)"
echo "==>       Run ./scripts/unity/submit_phase10_4.sh          (for full research suite)"
