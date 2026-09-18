#!/usr/bin/env bash
# Pull completed research outputs, model checkpoints, and logs from Unity to local
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_OUTPUTS="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/outputs/"
LOCAL_OUTPUTS="$(cd "$(dirname "$0")/../.." && pwd)/outputs/"

mkdir -p "$LOCAL_OUTPUTS"

echo "==> Pulling research outputs from Unity ($REMOTE_OUTPUTS) to local ($LOCAL_OUTPUTS)..."
rsync -avz "${REMOTE_HOST}:${REMOTE_OUTPUTS}" "$LOCAL_OUTPUTS"

echo "==> Pull complete."
