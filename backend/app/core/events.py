"""Server-Sent Events manager for real-time updates"""

import asyncio
import json
from typing import Dict, Any, AsyncGenerator
from datetime import datetime
import uuid


class EventManager:
    """Manages SSE connections and event broadcasting"""

    def __init__(self):
        self.connections: Dict[str, asyncio.Queue] = {}

    async def connect(self, client_id: str = None) -> str:
        """Create a new SSE connection"""
        if not client_id:
            client_id = str(uuid.uuid4())

        self.connections[client_id] = asyncio.Queue()
        return client_id

    async def disconnect(self, client_id: str):
        """Remove an SSE connection"""
        if client_id in self.connections:
            del self.connections[client_id]

    async def send_event(
        self,
        client_id: str,
        event: str,
        data: Any,
        event_id: str = None
    ):
        """Send an event to a specific client"""
        if client_id not in self.connections:
            return

        event_data = {
            "event": event,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        if event_id:
            event_data["id"] = event_id

        await self.connections[client_id].put(event_data)

    async def broadcast(self, event: str, data: Any):
        """Broadcast an event to all connected clients"""
        for client_id in self.connections:
            await self.send_event(client_id, event, data)

    async def stream(self, client_id: str) -> AsyncGenerator[str, None]:
        """Generate SSE stream for a client"""
        try:
            while True:
                # Send heartbeat every 30 seconds
                try:
                    event_data = await asyncio.wait_for(
                        self.connections[client_id].get(),
                        timeout=30
                    )

                    # Format SSE message
                    if event_data.get("event"):
                        yield f"event: {event_data['event']}\n"
                    if event_data.get("id"):
                        yield f"id: {event_data['id']}\n"
                    yield f"data: {json.dumps(event_data['data'])}\n\n"

                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield f"event: heartbeat\n"
                    yield f"data: {json.dumps({'timestamp': datetime.utcnow().isoformat()})}\n\n"

        except asyncio.CancelledError:
            await self.disconnect(client_id)
            raise


# Global event manager instance
event_manager = EventManager()