# Execution Authorization Specification (Phase F18)

## 1. Authority Separation
No trade may be transmitted to a broker without an immutable `ExecutionAuthorization` record produced by the deterministic risk pipeline.

## 2. Required Fields
- `authorization_id`: Unique identifier
- `timestamp`: ISO-8601 evaluation timestamp
- `symbol`: Target security
- `side`: BUY or SELL
- `quantity`: Approved shares
- `target_notional`: Dollar exposure ($)
- `is_authorized`: Boolean decision
- `rejection_reasons`: List of fail-closed codes if rejected
