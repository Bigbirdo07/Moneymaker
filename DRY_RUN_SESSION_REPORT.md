# Dry Run Forward Session Report (Phase F2)

## 1. Executive Summary & Governance Verdict
- **Session ID**: `DRYRUN_20260731_8a78b3`
- **Date**: `2026-07-31`
- **Execution Environment**: `ExecutionEnvironment.DRY_RUN`
- **Starting Strategy Capital**: `$1,000.00`
- **Broker Order Submissions**: `0 (Hard-blocked by DRY_RUN policy)`
- **Authorizations Generated**: `10`
- **Total Candidate Evaluations**: `10`
- **Operational Status**: `DRY_RUN_FORWARD_SESSION_COMPLETED`

## 2. Premarket Intelligence & Regime Analysis
```
------------------------------------------------------------
MONEYMAKER MORNING BRIEF

Date:
2026-07-31

Portfolio Equity:
$1,000.00

Capital Tier:
TIER_PAPER_1000

Portfolio Risk State:
NORMAL

Market Regime:
BULLISH_CONTINUATION

Session Gate:
GO

SPY Premarket:
+0.37%

Market Breadth:
67%

Volatility State:
NORMAL

Cross-Sectional Dispersion:
HIGH

Strongest Sectors:
1. Technology (+2.22%, Rel: +185 bps)
2. Software (+1.86%, Rel: +149 bps)
3. Communication Services (+0.93%, Rel: +56 bps)

Weakest Sectors:
1. Industrials (-1.23%)
2. Semiconductors (-2.39%)

Raw Listed Universe:
4812

Security-Type Eligible:
2945

Liquid Eligible:
826

Data-Quality Eligible:
803

Event Vetoes:
17

FastScanner Survivors:
15

Deep-Ranking Candidates:
12

Entry-Qualified Now:
0

Top Research Candidates:
1. GOOGL (Technology, Pre: +5.02%, RelVol: 3.3x) [CLEAR]
2. AMZN (Consumer Cyclical, Pre: +3.45%, RelVol: 3.5x) [CLEAR]
3. ACN (Technology, Pre: +3.39%, RelVol: 0.8x) [CLEAR]
4. CRM (Software, Pre: +3.31%, RelVol: 0.8x) [CLEAR]
5. MSFT (Technology, Pre: +2.74%, RelVol: 3.5x) [CLEAR]

Primary Risks Today:
- Standard market volatility

Current Decision:
NO TRADE

Reason:
No candidate currently exceeds required executable net-edge and risk criteria.
------------------------------------------------------------
```

## 3. Dynamic Universe & FastScanner Funnel
- **Total Market Universe**: 50
- **Structural Eligible**: 50
- **Liquid Tradable Symbols**: 50
- **Top 100 Selected**: 50
- **FastScanner Top Candidates**: 10

### Candidate Evaluations Table
| Symbol | Scanner Score | Predicted Edge (bps) | Cost (bps) | Net Edge (bps) | Confidence | Event Status | Authorized |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AMZN** | 0.510 | 25.3 | 7.1 | 18.2 | 0.63 | `ALLOW` | ✅ YES |
| **AAPL** | 0.510 | 25.3 | 7.1 | 18.2 | 0.63 | `ALLOW` | ✅ YES |
| **SPY** | 0.510 | 25.3 | 6.9 | 18.4 | 0.63 | `ALLOW` | ✅ YES |
| **NVDA** | 0.510 | 25.3 | 7.2 | 18.1 | 0.63 | `ALLOW` | ✅ YES |
| **MSFT** | 0.510 | 25.3 | 6.9 | 18.4 | 0.63 | `ALLOW` | ✅ YES |
| **GOOGL** | 0.510 | 25.3 | 7.1 | 18.2 | 0.63 | `ALLOW` | ✅ YES |
| **META** | 0.510 | 25.3 | 6.9 | 18.4 | 0.63 | `ALLOW` | ✅ YES |
| **INTC** | 0.510 | 25.3 | 7.8 | 17.5 | 0.63 | `ALLOW` | ✅ YES |
| **AMD** | 0.510 | 25.3 | 6.9 | 18.4 | 0.63 | `ALLOW` | ✅ YES |
| **TSLA** | 0.510 | 25.3 | 7.1 | 18.2 | 0.63 | `ALLOW` | ✅ YES |

## 4. Execution Authorizations & Decision Ledger
- **Authorizations Issued**: 10
- **Rejection Reasons Recorded**: 10

### Detailed Decision Records
| Timestamp | Symbol | Action | Reason Codes |
| :--- | :--- | :--- | :--- |
| 2026-09-18T06:27:52.315630+00:00 | **AMZN** | `AUTHORIZED_BUY` | `EDGE_SATISFIED_ALL_POLICIES_PASSED, DRY_RUN_NO_BROKER_SUBMISSION` |
| 2026-09-18T06:27:52.315854+00:00 | **AAPL** | `AUTHORIZED_BUY` | `EDGE_SATISFIED_ALL_POLICIES_PASSED, DRY_RUN_NO_BROKER_SUBMISSION` |
| 2026-09-18T06:27:52.316062+00:00 | **SPY** | `AUTHORIZED_BUY` | `EDGE_SATISFIED_ALL_POLICIES_PASSED, DRY_RUN_NO_BROKER_SUBMISSION` |
| 2026-09-18T06:27:52.316267+00:00 | **NVDA** | `AUTHORIZED_BUY` | `EDGE_SATISFIED_ALL_POLICIES_PASSED, DRY_RUN_NO_BROKER_SUBMISSION` |
| 2026-09-18T06:27:52.316464+00:00 | **MSFT** | `AUTHORIZED_BUY` | `EDGE_SATISFIED_ALL_POLICIES_PASSED, DRY_RUN_NO_BROKER_SUBMISSION` |
| 2026-09-18T06:27:52.316661+00:00 | **GOOGL** | `AUTHORIZED_BUY` | `EDGE_SATISFIED_ALL_POLICIES_PASSED, DRY_RUN_NO_BROKER_SUBMISSION` |
| 2026-09-18T06:27:52.316858+00:00 | **META** | `AUTHORIZED_BUY` | `EDGE_SATISFIED_ALL_POLICIES_PASSED, DRY_RUN_NO_BROKER_SUBMISSION` |
| 2026-09-18T06:27:52.317049+00:00 | **INTC** | `AUTHORIZED_BUY` | `EDGE_SATISFIED_ALL_POLICIES_PASSED, DRY_RUN_NO_BROKER_SUBMISSION` |
| 2026-09-18T06:27:52.317240+00:00 | **AMD** | `AUTHORIZED_BUY` | `EDGE_SATISFIED_ALL_POLICIES_PASSED, DRY_RUN_NO_BROKER_SUBMISSION` |
| 2026-09-18T06:27:52.317427+00:00 | **TSLA** | `AUTHORIZED_BUY` | `EDGE_SATISFIED_ALL_POLICIES_PASSED, DRY_RUN_NO_BROKER_SUBMISSION` |

## 5. Governance Verification Verdict
```
======================================================================
STAGE 1 VERDICT: DRY_RUN_FORWARD_SESSION_COMPLETED
REAL_MONEY_NOT_AUTHORIZED
BROKER_SUBMISSIONS_COUNT: 0
AUTHORIZATION_INTEGRITY: VALIDATED
======================================================================
```
