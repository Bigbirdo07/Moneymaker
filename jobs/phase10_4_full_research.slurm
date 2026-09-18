#!/usr/bin/env bash
#SBATCH --job-name=mm_phase10_4_research
#SBATCH --partition=uri-cpu
#SBATCH --cpus-per-task=32
#SBATCH --mem=96G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm_phase10_4_%j.log
#SBATCH --error=logs/slurm_phase10_4_%j.err

set -euo pipefail

EXPERIMENT_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
export EXPERIMENT_ID="EXP_REAL_V2_${EXPERIMENT_TIMESTAMP}"

echo "======================================================================"
echo "SLURM JOB: Phase 10.4 Real-Market Native Alpha Research & Engine V2"
echo "Job ID        : ${SLURM_JOB_ID:-LOCAL}"
echo "Experiment ID : ${EXPERIMENT_ID}"
echo "Node          : ${SLURMD_NODENAME:-LOCAL}"
echo "CPUs / Mem    : 32 CPUs / 96GB RAM"
echo "Start Time    : $(date)"
echo "======================================================================"

CONDA_ENV_PATH="/scratch4/workspace/alberto_paz_uri_edu-azera-voice/.conda/envs/azera-voice"
REMOTE_PROJECT_DIR="/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"

cd "$REMOTE_PROJECT_DIR"
mkdir -p logs data/processed/matrix_cache "artifacts/unity/phase10_4/${EXPERIMENT_ID}"

# Activate Conda Environment
echo "==> Activating Conda Environment: $CONDA_ENV_PATH"
source /opt/anaconda3/etc/profile.d/conda.sh 2>/dev/null || source /modules/apps/miniconda/etc/profile.d/conda.sh 2>/dev/null || true
export PATH="$CONDA_ENV_PATH/bin:$PATH"
export PYTHONPATH="$REMOTE_PROJECT_DIR"

echo "==> Python Interpreter: $(which python)"
python -c "import sys, sklearn, pandas, numpy, scipy; print('Environment OK:', sys.version)"

# Execute Phase 10.4 Master Research Pipeline
echo ""
echo "==> Launching Phase 10.4 Master Research Pipeline on Unity HPC..."
python -u scripts/run_phase10_4_research.py

# Package and copy top-level reports to experiment directory
echo ""
echo "==> Packaging reports, manifests, and logs into experiment bundle..."
cp REAL_*.md "artifacts/unity/phase10_4/${EXPERIMENT_ID}/reports/" 2>/dev/null || true
cp PHASE_10_4_REPORT.md "artifacts/unity/phase10_4/${EXPERIMENT_ID}/reports/" 2>/dev/null || true
cp REAL_ENGINE_V2_FREEZE_MANIFEST.json "artifacts/unity/phase10_4/${EXPERIMENT_ID}/" 2>/dev/null || true
cp "logs/slurm_phase10_4_${SLURM_JOB_ID}.log" "artifacts/unity/phase10_4/${EXPERIMENT_ID}/slurm.log" 2>/dev/null || true

# Write experiment manifest
cat <<EOF > "artifacts/unity/phase10_4/${EXPERIMENT_ID}/experiment_manifest.json"
{
  "experiment_id": "${EXPERIMENT_ID}",
  "slurm_job_id": "${SLURM_JOB_ID:-UNKNOWN}",
  "execution_node": "${SLURMD_NODENAME:-UNKNOWN}",
  "completed_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "cluster_host": "login7.unity.rc.umass.edu",
  "partition": "uri-cpu",
  "evidence_class": "SIMULATED_EXECUTION_ON_REAL_MARKET_DATA",
  "holdout_status": "AUGUST_2026_SEALED"
}
EOF

echo ""
echo "======================================================================"
echo "PHASE 10.4 CLUSTER RESEARCH WORKFLOW COMPLETED: $(date)"
echo "Artifact Bundle Ready at: ${REMOTE_PROJECT_DIR}/artifacts/unity/phase10_4/${EXPERIMENT_ID}/"
echo "======================================================================"
