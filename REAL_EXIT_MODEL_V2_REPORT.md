# Real-Market Exit Model V2 Specification Report

## 1. Exit Decision Logic
- **Hard Stop Loss**: **1.5%** (Immediate un-overridable stop)
- **Take Profit Target**: **3.0%**
- **Trailing Drawdown Lock**: **0.8%** from peak after +1.2% gain
- **Dynamic Signal Decay**: Exit if continuation edge falls below **-3.0 bps** after target horizon / 2
- **Max Holding Duration**: **90 minutes**
- **End of Session**: Mandatory flatten at 15:55:00 ET
