# Order Idempotency Architecture (Phases F19, F20)

## 1. Idempotency Key Formulation
`order_intent_id = SHA256(session_id + symbol + side + quantity + timestamp)[:16]`

## 2. Duplicate Prevention
Submitting an identical order intent multiple times returns the existing `BrokerOrder` without generating duplicate market transactions.
