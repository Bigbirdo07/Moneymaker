#!/usr/bin/env bash
# Synchronize local research codebase and datasets to Unity cluster
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/"
LOCAL_DIR="$(cd "$(dirname "$0")/../.." && pwd)/"

echo "==> Synchronizing local codebase to Unity: $REMOTE_DIR"
rsync -avz --exclude '.git' \
           --exclude '.venv' \
           --exclude '__pycache__' \
           --exclude 'node_modules' \
           --exclude '.pytest_cache' \
           --exclude 'workstation/dist' \
           "$LOCAL_DIR" "${REMOTE_HOST}:${REMOTE_DIR}"

echo "==> Sync to Unity complete."
