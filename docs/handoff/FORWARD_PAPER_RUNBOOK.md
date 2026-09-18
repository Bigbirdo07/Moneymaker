# MONEYMAKER FORWARD PAPER OPERATIONAL RUNBOOK

This runbook defines standard operating procedures for executing and monitoring autonomous true forward paper trading sessions on the Unity HPC cluster.

---

## 1. Pre-Session Checklist (Run at ~08:15–08:25 ET)

Before launching any forward paper session, perform the following verification:

1. **Git Working Tree**:
   ```bash
   git status
   git log -n 1 --oneline
   ```
   *Requirement*: Working tree must be clean on `main` branch.

2. **Policy Hash Integrity**:
   ```bash
   python -c "
   import hashlib
   with open('FORWARD_PAPER_POLICY_V1.yaml', 'rb') as f:
       h = hashlib.sha256(f.read()).hexdigest()
   assert h == '9c2bc9f33a931f822fbd0574bbe28d7deefc87fb1da741604d3eec8207e0cb3b', f'Policy hash mismatch: {h}'
   print('Policy hash verified:', h)
   "
   ```

3. **Alpaca Paper Credentials**:
   - Ensure `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY` are configured in `.env` (or environment).
   - Ensure `APCA_API_BASE_URL` points to `https://paper-api.alpaca.markets`.

4. **Trading Calendar Verification**:
   - Confirm the target date is a regular U.S. trading session.

---

## 2. Launching Forward Sessions on Unity HPC

### Method A: Automated Morning Scheduler (Recommended)
This method enters a local timer loop until 08:25 ET, synchronizes the repository to Unity over SSH, and submits the Slurm job exactly when pre-market begins (preventing idle overnight node holding):

```bash
python scripts/unity/schedule_morning_launch.py --time 08:25:00 --mode wait_and_submit
```

### Method B: Direct Immediate Submission
To sync code and submit the Slurm batch job immediately for a target date:

```bash
./scripts/unity/submit_true_forward_session.sh 2026-09-21
```

---

## 3. Monitoring & Intraday Supervision

1. **Check Job Status and Tail Slurm Output**:
   ```bash
   ./scripts/unity/check_true_forward_session.sh <JOB_ID>
   ```

2. **Direct SSH Queue Check**:
   ```bash
   ssh unity "squeue -u \$USER"
   ```

3. **Follow Real-Time Execution Logs on Unity**:
   ```bash
   ssh unity "tail -f /scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM/logs/slurm_true_forward_<JOB_ID>.log"
   ```

---

## 4. Emergency Procedures & Killswitch

### When to Intervene:
- Order loop detected (multiple unintended orders submitted).
- Strategy capital breach (notional exceeds $750 or risk exceeds $7.50).
- Open position remains past 15:55 ET (flatten failure).
- Critical unhandled exception or connection loss.

### When NOT to Intervene:
- An open trade is showing a temporary unrealized loss (managed by stop-loss).
- No trades have been placed by midday (market regime / gate is doing its job).
- A top candidate was rejected due to the 30 bps hurdle.

### Emergency Halt Steps:
1. **Cancel the Slurm Job**:
   ```bash
   ssh unity "scancel <JOB_ID>"
   ```
2. **Emergency Flatten (if position is open in Alpaca)**:
   ```bash
   python -m src.safety.live_guard --emergency-halt
   ```

---

## 5. Post-Close Reconciliation & Artifact Retrieval (16:05 ET)

Once the market closes and the Slurm job completes:

1. **Pull Session Artifacts from Unity**:
   ```bash
   ./scripts/unity/pull_true_forward_session.sh
   ```

2. **Inspect Session Report**:
   ```bash
   cat artifacts/forward/TRUE_FORWARD_<DATE>_*/TRUE_FORWARD_SESSION_REPORT.md
   ```

3. **Verify 100% Flat & Clean Reconciliation**:
   - Check `true_forward_reconciliation.parquet`.
   - Confirm `eod_position_status == 100% FLAT (CASH)`.
   - Confirm `counts_toward_forward_block == TRUE`.

4. **Commit and Push Forward Artifacts**:
   ```bash
   git add artifacts/forward/
   git commit -m "feat(forward): record completed true forward paper session for <DATE>"
   git push origin main
   ```
