# Live Safety Architecture & Multi-Factor Arming Specification (Phase 4)

## 1. Executive Summary

Live money execution carries existential operational risk. Even if future pilot capital is authorized, **the Moneymaker platform implements a multi-layer defense-in-depth safety architecture** designed to make accidental live execution, unauthorized account access, or uncontrolled runaway trading mathematically impossible.

---

## 2. Multi-Factor Live Arming Protocol

No single configuration setting or environment variable can enable live execution. Live trading requires satisfying **six independent cryptographic and operational conditions**:

```
                              MULTI-FACTOR LIVE ARMING GATES
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Gate 1: Explicit Live Config Flag (`execution_mode: "LIVE"`)                          │
│ Gate 2: Capital Ceiling Lock (Approved capital <= MAX_LIVE_CAPITAL_USD)                │
│ Gate 3: Broker Account ID Lock (Exact match with single dedicated pilot account)      │
│ Gate 4: Pinned Risk Policy Hash Match (SHA-256 hash of immutable risk policy)         │
│ Gate 5: Human Arming Token (Cryptographic token provided by designated risk officer)   │
│ Gate 6: Daily Session Auth Token (Time-bounded token expiring at market close)         │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                     All 6 Gates Valid ─────┴───── Any Single Gate Fails
                            │                               │
                            ▼                               ▼
                      ARMED (LIVE)                  FATAL SHUTDOWN (CLOSED)
```

---

## 3. Hard Capital Firewall & Order Limits

| Firewall Layer | Hard Limit | Enforcement Mechanism |
| :--- | :--- | :--- |
| **`MAX_LIVE_CAPITAL_USD`** | **$2,500.00 USD** | Orders causing total account exposure $> \$2,500$ are hard-rejected. |
| **`MAX_SINGLE_ORDER_USD`** | **$250.00 USD** | Any order notional $> \$250$ is rejected prior to broker transmission. |
| **`MAX_ARCHETYPE_EXPOSURE`**| **20.0% ($500.00)** | Caps total high-beta correlated exposure across NVDA, AMD, TSLA. |
| **`MAX_CONCURRENT_POSITIONS`**| **3 positions** | Risk engine drops candidate signals when 3 positions are open. |

---

## 4. API Permission Minimization & Credential Isolation

To prevent catastrophic security breaches:

1. **Least-Privilege API Keys**:
   - **Permitted**: `read_account`, `read_orders`, `read_positions`, `submit_order`, `cancel_order`.
   - **Strictly Prohibited**: `withdraw_funds`, `transfer_funds`, `change_bank_instructions`, `modify_account_settings`.
2. **Physically Separated Credential Domains**:
   - Paper trading credentials (`PAPER_API_KEY`) and Live credentials (`LIVE_API_KEY`) reside in completely separate configuration paths and environment namespaces.
   - The platform never permits automated fallback between domains.

---

## 5. Exclusive Process Execution Lock

To prevent duplicate processes from trading the same account simultaneously:
- At startup, the `LiveSafetyGuard` attempts to acquire an exclusive file lock (`/tmp/moneymaker_live_execution.lock`) storing PID and timestamp.
- If a secondary instance attempts to launch, lock acquisition fails, and the process aborts immediately.

---

## 6. Manual Approval Mode (`LIVE_MANUAL_APPROVAL`) & Latency Impact

For high-assurance deployments, the system supports a **Human-in-the-Loop Manual Approval Mode**:
1. Model generates proposed trade.
2. Risk engine validates and approves parameters.
3. System prompts operator interface with order details.
4. Operator has a **30-second response window** to click APPROVE.
5. If operator responds in $>30\text{ seconds}$, order is marked `EXPIRED_OPERATOR_TIMEOUT` and discarded.

### Latency Trade-Off Analysis:
- An operator latency of **10–15 seconds** consumes ~0.5 bps of the 4.8 bps gross alpha.
- Because gross edge is +4.8 bps, the strategy **remains net profitable (+0.95 bps/trade)** even with manual operator confirmation, proving that safety does not require sacrificing quantitative viability.
