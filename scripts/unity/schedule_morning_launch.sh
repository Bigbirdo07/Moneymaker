#!/bin/bash
# ==============================================================================
# SCHEDULE TRUE FORWARD SESSION MORNING LAUNCH ON UNITY HPC
# ==============================================================================
set -euo pipefail

SESSION_DATE="${1:-}"
MODE="${2:-wait_and_submit}"

if [ -n "${SESSION_DATE}" ]; then
    python scripts/unity/schedule_morning_launch.py --date "${SESSION_DATE}" --mode "${MODE}"
else
    python scripts/unity/schedule_morning_launch.py --mode "${MODE}"
fi
