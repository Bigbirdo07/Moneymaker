# End-of-Day Flattening Policy (Phases F33, F34)

## 1. Flattening Window
- **Start Flattening**: **15:45:00 ET** (or 15 minutes before early close).
- **Target Flat**: **15:55:00 ET**.
- **Market Close**: **16:00:00 ET**.

## 2. Overnight Exposure Invariant
Moneymaker has **zero intentional overnight equity risk**. Any position unable to close due to halt or market failure is flagged as an `UNPLANNED_OVERNIGHT_EXPOSURE` incident.
