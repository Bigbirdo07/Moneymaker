"""
Moneymaker Workstation Streaming & Real-Time Event Hub.
Manages WebSocket connections and server-sent telemetry broadcasts
for prices, portfolio equity, orders, fills, and risk alerts.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Set
from fastapi import WebSocket


class WorkstationStreamingHub:
    """
    Broadcasts live market and portfolio events to connected frontends.
    """

    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Sends a JSON event payload to all active client connections."""
        if not self.active_connections:
            return

        payload = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        raw_msg = json.dumps(payload)
        stale_connections = []

        for ws in self.active_connections:
            try:
                await ws.send_text(raw_msg)
            except Exception:
                stale_connections.append(ws)

        for stale in stale_connections:
            self.active_connections.discard(stale)


# Global singleton instance
streaming_hub = WorkstationStreamingHub()
