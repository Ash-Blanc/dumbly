# backend/app/services/stream_manager.py

from fastapi import WebSocket
from typing import Dict, Set
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class StreamConnection:
    websocket: WebSocket
    analysis_id: str
    subscribed_events: Set[str] = field(default_factory=lambda: {"progress", "step", "thought", "error", "complete"})


class StreamManager:
    """Manages WebSocket connections and broadcasts updates"""

    def __init__(self):
        self._connections: Dict[str, StreamConnection] = {}
        self._event_queues: Dict[str, asyncio.Queue] = {}

    async def connect(self, websocket: WebSocket, analysis_id: str):
        """Register a new WebSocket connection"""
        await websocket.accept()
        self._connections[analysis_id] = StreamConnection(
            websocket=websocket,
            analysis_id=analysis_id,
        )
        self._event_queues[analysis_id] = asyncio.Queue()

        # Start broadcasting task
        asyncio.create_task(self._broadcast_loop(analysis_id))

    def disconnect(self, analysis_id: str):
        """Remove a WebSocket connection"""
        self._connections.pop(analysis_id, None)
        self._event_queues.pop(analysis_id, None)

    async def emit(self, analysis_id: str, event_type: str, data: dict):
        """Emit an event to a specific analysis stream"""
        if analysis_id in self._event_queues:
            event = {
                "type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            await self._event_queues[analysis_id].put(event)

    async def emit_all(self, event_type: str, data: dict):
        """Broadcast to all connected clients"""
        for analysis_id in self._connections:
            await self.emit(analysis_id, event_type, data)

    async def _broadcast_loop(self, analysis_id: str):
        """Continuously broadcast events to the WebSocket"""
        queue = self._event_queues.get(analysis_id)
        connection = self._connections.get(analysis_id)

        if not queue or not connection:
            return

        try:
            while True:
                event = await queue.get()
                await connection.websocket.send_json(event)
        except Exception:
            self.disconnect(analysis_id)


# Singleton instance
stream_manager = StreamManager()
