from fastapi import WebSocket
from typing import List
import logging
import asyncio

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time frontend dashboard streaming."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.debug(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.debug(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        """Send a string/JSON message to all connected clients concurrently."""
        if not self.active_connections:
            return
            
        tasks = []
        for connection in self.active_connections:
            # We catch exceptions per-connection so one broken pipe doesn't crash the loop
            tasks.append(self._safely_send(connection, message))
        
        await asyncio.gather(*tasks)
        
    async def _safely_send(self, websocket: WebSocket, message: str):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.debug(f"Failed to send to websocket: {e}")
            try:
                self.disconnect(websocket)
            except ValueError:
                pass
