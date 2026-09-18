# Failure Recovery & Emergency Kill Switch (Phases F27, F73)

## 1. Emergency Kill Switch Actions
- Immediate cancellation of all open entry orders.
- Halting of the trading state machine (`RuntimeState.HALTED`).
- Automated liquidation of un-halted open positions.

## 2. Trapped Halt Handling
Positions halted by the exchange are transitioned to `HALTED_TRAPPED` and monitored until market resumption without generating fictitious fills.
