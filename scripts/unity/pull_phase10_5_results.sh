#!/usr/bin/env bash
# Pull Phase 10.5 Final Holdout Results from Unity to local Mac

set -euo pipefail

EXPERIMENT_ID="${1:-}"
REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="/Users/albertopaz/Moneymaker"

if [ -z "$EXPERIMENT_ID" ]; then
    echo "==> No Experiment ID supplied. Finding latest Phase 10.5 experiment on Unity..."
    LATEST_EXP=$(ssh "$REMOTE_HOST" "ls -td '$REMOTE_DIR'/artifacts/unity/phase10_5/PHASE10_5_FINAL_* 2>/dev/null | head -n 1")
    if [ -z "$LATEST_EXP" ]; then
        echo "ERROR: No Phase 10.5 experiments found on Unity."
        exit 1
    fi
    EXPERIMENT_ID=$(basename "$LATEST_EXP")
fi

REMOTE_EXP_DIR="${REMOTE_DIR}/artifacts/unity/phase10_5/${EXPERIMENT_ID}/"
LOCAL_EXP_DIR="${LOCAL_DIR}/artifacts/unity/phase10_5/${EXPERIMENT_ID}/"

echo "======================================================================"
echo "PULLING PHASE 10.5 FINAL HOLDOUT RESULTS FROM UNITY HPC"
echo "Experiment ID : $EXPERIMENT_ID"
echo "Remote Source : $REMOTE_EXP_DIR"
echo "Local Target  : $LOCAL_EXP_DIR"
echo "======================================================================"

mkdir -p "$LOCAL_EXP_DIR"

echo "==> [1/3] Syncing experiment artifacts (ledgers, reports, manifests, logs)..."
rsync -avz --progress \
    --include="*.md" \
    --include="*.json" \
    --include="*.parquet" \
    --include="*.log" \
    --include="*/" \
    --exclude="*" \
    "${REMOTE_HOST}:${REMOTE_EXP_DIR}" "$LOCAL_EXP_DIR"

echo "==> [2/3] Updating root workspace reports..."
if [ -d "${LOCAL_EXP_DIR}reports" ]; then
    cp -v "${LOCAL_EXP_DIR}reports/"*.md "$LOCAL_DIR/" 2>/dev/null || true
fi
if [ -f "${LOCAL_EXP_DIR}FINAL_AUGUST_METRICS.json" ]; then
    cp -v "${LOCAL_EXP_DIR}FINAL_AUGUST_METRICS.json" "$LOCAL_DIR/" 2>/dev/null || true
fi
if [ -f "${LOCAL_EXP_DIR}FINAL_HOLDOUT_FREEZE_VERIFICATION.json" ]; then
    cp -v "${LOCAL_EXP_DIR}FINAL_HOLDOUT_FREEZE_VERIFICATION.json" "$LOCAL_DIR/" 2>/dev/null || true
fi
if [ -f "${LOCAL_EXP_DIR}PHASE_10_5_PROVENANCE.json" ]; then
    cp -v "${LOCAL_EXP_DIR}PHASE_10_5_PROVENANCE.json" "$LOCAL_DIR/" 2>/dev/null || true
fi

echo "==> [3/3] Pulled Artifact Summary:"
ls -lh "$LOCAL_EXP_DIR"

echo ""
echo "======================================================================"
echo "PHASE 10.5 RESULTS RETRIEVED SUCCESSFULLY"
echo "Reports available in: ${LOCAL_EXP_DIR}reports/"
echo "======================================================================"
