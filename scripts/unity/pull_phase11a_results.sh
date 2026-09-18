#!/bin/bash
# ==============================================================================
# PULL PHASE 11A RESEARCH RESULTS FROM UMASS AMHERST UNITY HPC TO LOCAL MAC
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="/Users/albertopaz/Moneymaker"
EXPERIMENT_ID="${1:-}"

if [ -z "${EXPERIMENT_ID}" ]; then
    echo "==> No Experiment ID supplied. Finding latest Phase 11A experiment on Unity..."
    EXPERIMENT_ID=$(ssh ${REMOTE_HOST} "ls -td ${REMOTE_DIR}/artifacts/unity/phase11a/PHASE11A_* 2>/dev/null | head -n 1 | xargs -n 1 basename || true")
    if [ -z "${EXPERIMENT_ID}" ]; then
        echo "ERROR: No Phase 11A experiments found on Unity."
        exit 1
    fi
fi

REMOTE_EXP_DIR="${REMOTE_DIR}/artifacts/unity/phase11a/${EXPERIMENT_ID}"
LOCAL_EXP_DIR="${LOCAL_DIR}/artifacts/unity/phase11a/${EXPERIMENT_ID}"

echo "======================================================================"
echo "PULLING PHASE 11A WALK-FORWARD RESULTS FROM UNITY HPC"
echo "Experiment ID : ${EXPERIMENT_ID}"
echo "Remote Source : ${REMOTE_EXP_DIR}/"
echo "Local Target  : ${LOCAL_EXP_DIR}/"
echo "======================================================================"

mkdir -p "${LOCAL_EXP_DIR}"

# Step 1: Pull artifact files
echo "==> [1/3] Syncing experiment artifacts (reports, ledgers, JSONs)..."
rsync -avz \
    --include="*/" \
    --include="*.md" \
    --include="*.json" \
    --include="*.parquet" \
    --include="*.log" \
    --exclude="*" \
    "${REMOTE_HOST}:${REMOTE_EXP_DIR}/" "${LOCAL_EXP_DIR}/"

# Step 2: Copy top-level reports to workspace root
echo "==> [2/3] Updating root workspace reports..."
if [ -d "${LOCAL_EXP_DIR}/reports" ]; then
    for report_file in "${LOCAL_EXP_DIR}/reports"/*.md; do
        if [ -f "${report_file}" ]; then
            base_name=$(basename "${report_file}")
            cp -v "${report_file}" "${LOCAL_DIR}/${base_name}"
        fi
    done
fi

if [ -f "${LOCAL_EXP_DIR}/PHASE_11A_MONTHLY_METRICS.json" ]; then
    cp -v "${LOCAL_EXP_DIR}/PHASE_11A_MONTHLY_METRICS.json" "${LOCAL_DIR}/PHASE_11A_MONTHLY_METRICS.json"
fi

if [ -f "${LOCAL_EXP_DIR}/PHASE_11A_PROVENANCE.json" ]; then
    cp -v "${LOCAL_EXP_DIR}/PHASE_11A_PROVENANCE.json" "${LOCAL_DIR}/PHASE_11A_PROVENANCE.json"
fi

# Step 3: Summary of pulled artifacts
echo "==> [3/3] Pulled Artifact Summary:"
ls -lh "${LOCAL_EXP_DIR}"

echo ""
echo "======================================================================"
echo "PHASE 11A RESULTS RETRIEVED SUCCESSFULLY"
echo "Reports available in: ${LOCAL_EXP_DIR}/reports/"
echo "======================================================================"
