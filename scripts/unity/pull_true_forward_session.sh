#!/bin/bash
# ==============================================================================
# PULL TRUE FORWARD PAPER SESSION ARTIFACTS FROM UNITY HPC
# ==============================================================================
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"
LOCAL_DIR="./artifacts/forward"

mkdir -p "${LOCAL_DIR}"

echo "======================================================================"
echo "SYNCHRONIZING TRUE FORWARD ARTIFACTS FROM UNITY HPC"
echo "======================================================================"

rsync -avz --progress \
    ${REMOTE_HOST}:${REMOTE_DIR}/artifacts/forward/ \
    ${LOCAL_DIR}/

echo ""
echo "==> Local Forward Artifacts:"
ls -la ${LOCAL_DIR}

echo ""
echo "======================================================================"
echo "TRUE FORWARD ARTIFACTS SYNCHRONIZED SUCCESSFULLY"
echo "======================================================================"
