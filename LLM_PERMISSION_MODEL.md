# Moneymaker Research Director: LLM Permission Model & Security Isolation

## 1. Security Mandate & Isolation Rules
The Moneymaker Quantitative Research Platform enforces an absolute boundary between LLM inference and capital execution. Under no circumstances may an LLM component hold execution permissions or write access to trading parameters.

---

## 2. Permission Matrix

| Capability / Resource | LLM Research Director | Human Operator | Quantitative Model Pipeline |
| :--- | :--- | :--- | :--- |
| **View Session Summaries** | **ALLOWED (Read-Only)**| ALLOWED | ALLOWED |
| **View Risk & Drift Metrics**| **ALLOWED (Read-Only)**| ALLOWED | ALLOWED |
| **Query RAG Knowledge Base** | **ALLOWED (Read-Only)**| ALLOWED | N/A |
| **Propose Challenger Hypotheses**| **ALLOWED (Advisory)**| ALLOWED | N/A |
| **Submit Broker Orders** | **STRICTLY PROHIBITED**| ALLOWED (Governed) | PROHIBITED (Unapproved) |
| **Cancel Resting Orders** | **STRICTLY PROHIBITED**| ALLOWED | ALLOWED (Deterministic Risk) |
| **Modify Risk Limits** | **STRICTLY PROHIBITED**| PROHIBITED (Frozen)| PROHIBITED |
| **Retrain Champion Models** | **STRICTLY PROHIBITED**| PROHIBITED (Frozen)| PROHIBITED |
| **Access Broker Credentials**| **STRICTLY PROHIBITED**| RESTRICTED (Vault) | PROHIBITED (Injected Gateway)|
| **Initiate Withdrawals / Transfers**| **STRICTLY PROHIBITED**| PROHIBITED | PROHIBITED |

---

## 3. Enforcement Mechanisms

1. **Interface Isolation**: The `MoneymakerResearchDirector` class in `src/llm/research_director.py` has no imports or reference handles to `BrokerAdapter.submit_order` or `BrokerAdapter.execute_fill`.
2. **Permission Guard**: `verify_permission_boundary()` performs fail-closed verification before generating any output.
3. **Credential Isolation**: Broker API keys and arming secrets are stored in secure environment variables and never passed to the LLM context.
4. **Champion Immutability**: Champion configuration (`configs/frozen_phase5a.yaml`) is cryptographically hash-pinned on session arming. Any attempt by an external script to modify it causes immediate session arming failure.
