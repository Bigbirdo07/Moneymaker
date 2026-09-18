#!/usr/bin/env bash
# Bootstrap Moneymaker folder structure and environment on Unity
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"

echo "==> Creating canonical directory tree on Unity: $REMOTE_DIR"
ssh "$REMOTE_HOST" "mkdir -p $REMOTE_DIR/{src,scripts,data,logs,outputs,configs,experiments,jobs,models,embeddings,reports,artifacts,checkpoints}"

echo "==> Verifying cross-mount read access to shared Qwen model and Conda env..."
ssh "$REMOTE_HOST" "ls -d /scratch4/workspace/alberto_paz_uri_edu-azera-voice/.cache/huggingface/hub/models--Qwen--Qwen2.5-14B-Instruct/snapshots/* && ls -d /scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"

echo "==> Bootstrap verified successfully."
