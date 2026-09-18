#!/usr/bin/env bash
# Pull Phase 10.4 research models, reports, metrics, and freeze manifests from Unity HPC
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

EXP_ID="${1:-}"

if [ -z "$EXP_ID" ]; then
    echo "==> Discovering latest Phase 10.4 experiment on Unity..."
    LATEST_EXP=$(ssh "$REMOTE_HOST" "ls -td $REMOTE_DIR/artifacts/unity/phase10_4/EXP_REAL_V2_* 2>/dev/null | head -n1 | xargs -n1 basename || true")
    if [ -z "$LATEST_EXP" ]; then
        echo "ERROR: No Phase 10.4 experiments found on Unity under $REMOTE_DIR/artifacts/unity/phase10_4/"
        exit 1
    fi
    EXP_ID="$LATEST_EXP"
fi

echo "======================================================================"
echo "PULLING PHASE 10.4 RESULTS FROM UNITY HPC"
echo "Experiment ID : $EXP_ID"
echo "Remote Source : $REMOTE_DIR/artifacts/unity/phase10_4/$EXP_ID/"
echo "Local Target  : $LOCAL_DIR/artifacts/unity/phase10_4/$EXP_ID/"
echo "======================================================================"

mkdir -p "$LOCAL_DIR/artifacts/unity/phase10_4/$EXP_ID"

# 1. Pull experiment bundle (excluding huge raw matrices)
echo "==> [1/3] Syncing experiment artifacts (models, reports, manifests, logs)..."
rsync -avz \
    --exclude '*.parquet' \
    --exclude 'matrix_cache/' \
    "${REMOTE_HOST}:${REMOTE_DIR}/artifacts/unity/phase10_4/${EXP_ID}/" \
    "$LOCAL_DIR/artifacts/unity/phase10_4/${EXP_ID}/"

# 2. Mirror latest markdown reports to root workspace for direct viewing
echo "==> [2/3] Updating root workspace reports and freeze manifest..."
if [ -d "$LOCAL_DIR/artifacts/unity/phase10_4/${EXP_ID}/reports" ]; then
    cp "$LOCAL_DIR/artifacts/unity/phase10_4/${EXP_ID}/reports/"*.md "$LOCAL_DIR/" 2>/dev/null || true
fi
if [ -f "$LOCAL_DIR/artifacts/unity/phase10_4/${EXP_ID}/REAL_ENGINE_V2_FREEZE_MANIFEST.json" ]; then
    cp "$LOCAL_DIR/artifacts/unity/phase10_4/${EXP_ID}/REAL_ENGINE_V2_FREEZE_MANIFEST.json" "$LOCAL_DIR/" 2>/dev/null || true
fi

# 3. Print verification
echo "==> [3/3] Pulled Artifact Summary:"
ls -la "$LOCAL_DIR/artifacts/unity/phase10_4/${EXP_ID}"

echo ""
echo "======================================================================"
echo "PHASE 10.4 RESULTS RETRIEVED SUCCESSFULLY"
echo "Reports available in: $LOCAL_DIR/artifacts/unity/phase10_4/${EXP_ID}/reports/"
echo "======================================================================"
