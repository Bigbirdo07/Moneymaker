#!/bin/bash
set -euo pipefail

REMOTE_HOST="unity"
REMOTE_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"

echo "======================================================================"
echo "PULLING PHASE F2 / F3 ARTIFACTS FROM UNITY HPC"
echo "======================================================================"

scp ${REMOTE_HOST}:${REMOTE_DIR}/DRY_RUN_SESSION_REPORT.md ./
scp ${REMOTE_HOST}:${REMOTE_DIR}/FIRST_FORWARD_PAPER_SESSION_REPORT.md ./
scp ${REMOTE_HOST}:${REMOTE_DIR}/FIRST_FORWARD_PAPER_PROVENANCE.json ./
scp ${REMOTE_HOST}:${REMOTE_DIR}/forward_paper_decisions.parquet ./
scp ${REMOTE_HOST}:${REMOTE_DIR}/forward_paper_order_intents.parquet ./
scp ${REMOTE_HOST}:${REMOTE_DIR}/forward_paper_orders.parquet ./
scp ${REMOTE_HOST}:${REMOTE_DIR}/forward_paper_fills.parquet ./
scp ${REMOTE_HOST}:${REMOTE_DIR}/forward_paper_positions.parquet ./
scp ${REMOTE_HOST}:${REMOTE_DIR}/forward_runtime_events.parquet ./
scp ${REMOTE_HOST}:${REMOTE_DIR}/forward_operational_incidents.parquet ./
scp ${REMOTE_HOST}:${REMOTE_DIR}/forward_reconciliation.parquet ./

echo "Sync complete."
