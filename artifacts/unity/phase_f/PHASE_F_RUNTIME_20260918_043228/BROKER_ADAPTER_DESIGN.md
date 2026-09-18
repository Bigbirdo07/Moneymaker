# Broker Adapter Interface & Implementations (Phase F4)

## 1. Abstract Broker Adapter Interface
The `BrokerAdapter` abstracts low-level broker communication:
- `get_account()`: Verified paper balance, cash, and equity.
- `get_positions()`: Active open positions.
- `get_open_orders()`: Outstanding pending orders.
- `submit_order(intent)`: Idempotent order execution.
- `cancel_order(order_id)`: Active order cancellation.
- `close_position(symbol)`: Single symbol liquidation.
- `close_all_positions()`: Emergency or EOD portfolio liquidation.

## 2. Supported Adapters
1. **SimulationBrokerAdapter**: Hermetic in-memory execution simulator for offline verification.
2. **AlpacaPaperBrokerAdapter**: Bound strictly to `https://paper-api.alpaca.markets`.
