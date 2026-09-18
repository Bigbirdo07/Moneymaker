#!/usr/bin/env python3
"""
======================================================================
MONEYMAKER UNITY MORNING LAUNCH SCHEDULER
======================================================================
Ensures no idle compute nodes are held overnight on the Unity cluster.
Supports:
1. 'wait_and_submit' (Default): Waits locally until 08:25/08:30 ET on the
   target session date, then sends the sbatch command over SSH right when
   market premarket begins. Zero cluster resources used beforehand.
2. 'slurm_begin': Submits immediately with `--begin=YYYY-MM-DDTHH:MM:SS`
   so Slurm holds the job in PENDING state (0 CPU, 0 RAM, 0 node hours).
======================================================================
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import zoneinfo
from datetime import date, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.data.calendar import ET_TZ, UTC_TZ, TradingCalendar

REMOTE_HOST = "unity"
REMOTE_DIR = "/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM"


def get_next_market_morning(target_date_str: str | None = None, target_time_str: str = "08:25:00") -> datetime:
    """Calculates the target datetime in America/New_York."""
    tc = TradingCalendar()
    if target_date_str:
        d = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    else:
        now_et = datetime.now(ET_TZ)
        d = now_et.date()
        # If today is already past 08:30 ET or not a trading day, advance to next trading day
        t_hour, t_min, t_sec = map(int, target_time_str.split(":"))
        target_today = datetime(d.year, d.month, d.day, t_hour, t_min, t_sec, tzinfo=ET_TZ)
        if not tc.is_trading_day(d) or now_et >= target_today:
            d = d + timedelta(days=1)
            while not tc.is_trading_day(d):
                d = d + timedelta(days=1)

    t_hour, t_min, t_sec = map(int, target_time_str.split(":"))
    return datetime(d.year, d.month, d.day, t_hour, t_min, t_sec, tzinfo=ET_TZ)


def run_sync_to_unity() -> None:
    """Synchronizes codebase to Unity before launching."""
    print("==> Synchronizing codebase to Unity HPC...")
    cmd = [
        "rsync", "-avz",
        "--exclude", ".git",
        "--exclude", ".venv",
        "--exclude", "node_modules",
        "--exclude", "workstation/node_modules",
        "--exclude", "__pycache__",
        "--exclude", "*.pyc",
        "--exclude", ".pytest_cache",
        "--exclude", "data/raw",
        "--exclude", "artifacts/unity",
        f"{REPO_ROOT}/", f"{REMOTE_HOST}:{REMOTE_DIR}/",
    ]
    subprocess.run(cmd, check=True)


def submit_slurm_job(session_date: str, begin_time: str | None = None) -> str:
    """Executes sbatch on Unity over SSH."""
    begin_flag = f"--begin={begin_time} " if begin_time else ""
    remote_cmd = f"cd {REMOTE_DIR} && sbatch {begin_flag}jobs/true_forward_paper_session.slurm {session_date}"
    print(f"==> Executing remote command: {remote_cmd}")
    res = subprocess.run(
        ["ssh", REMOTE_HOST, remote_cmd],
        capture_output=True,
        text=True,
        check=True,
    )
    print(res.stdout.strip())
    return res.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description="Schedule Slurm true forward session launch on Unity.")
    parser.add_argument("--date", type=str, default=None, help="Target session date (YYYY-MM-DD)")
    parser.add_argument("--time", type=str, default="08:25:00", help="Trigger time ET (default: 08:25:00)")
    parser.add_argument(
        "--mode",
        choices=["wait_and_submit", "slurm_begin", "now"],
        default="wait_and_submit",
        help="Scheduling mode: 'wait_and_submit' (local timer until 08:25 ET), 'slurm_begin' (deferred sbatch), or 'now' (submit immediately)",
    )
    args = parser.parse_args()

    target_dt = get_next_market_morning(args.date, args.time)
    session_date = target_dt.strftime("%Y-%m-%d")

    print("======================================================================")
    print("MONEYMAKER TRUE FORWARD SLURM SCHEDULER")
    print("======================================================================")
    print(f"Target Session Date : {session_date}")
    print(f"Target Launch Time  : {target_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Scheduling Mode     : {args.mode}")
    print("======================================================================")

    # 1. Sync first
    run_sync_to_unity()

    if args.mode == "now":
        print("==> Submitting Slurm job immediately...")
        submit_slurm_job(session_date)
        return

    if args.mode == "slurm_begin":
        # Format begin time for Slurm: YYYY-MM-DDTHH:MM:SS
        slurm_begin_str = target_dt.strftime("%Y-%m-%dT%H:%M:%S")
        print(f"==> Submitting to Slurm with deferred allocation: --begin={slurm_begin_str}")
        print("    (Job will remain PENDING with 0 CPU / 0 RAM usage until scheduled time)")
        submit_slurm_job(session_date, begin_time=slurm_begin_str)
        return

    if args.mode == "wait_and_submit":
        print(f"==> Entering local wait loop until {target_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}...")
        print("    (Zero cluster nodes/resources will be held until the trigger time)")
        while True:
            now_et = datetime.now(ET_TZ)
            remaining_sec = (target_dt - now_et).total_seconds()
            if remaining_sec <= 0:
                print(f"\n==> [TRIGGER REACHED {now_et.strftime('%H:%M:%S %Z')}] Submitting Slurm job to Unity now!")
                submit_slurm_job(session_date)
                break
            
            hrs, rem = divmod(int(remaining_sec), 3600)
            mins, secs = divmod(rem, 60)
            sys.stdout.write(f"\r==> Time remaining until launch: {hrs:02d}h {mins:02d}m {secs:02d}s (Current ET: {now_et.strftime('%H:%M:%S')}) ")
            sys.stdout.flush()
            sleep_step = min(remaining_sec, 10.0 if remaining_sec > 60 else 1.0)
            time.sleep(sleep_step)


if __name__ == "__main__":
    main()
