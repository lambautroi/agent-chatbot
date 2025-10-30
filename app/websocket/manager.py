from typing import Dict, List
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        # Mapping conversation_id -> list of active WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, conversation_id: int, websocket: WebSocket):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)
        print(f"🔗 Client connected to conversation {conversation_id}")

    def disconnect(self, conversation_id: int, websocket: WebSocket):
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]
        print(f"Client disconnected from conversation {conversation_id}")

    async def broadcast(self, conversation_id: int, message: dict):
        if conversation_id in self.active_connections:
            disconnected_clients = []
            for connection in self.active_connections[conversation_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    disconnected_clients.append(connection)
            # clean up dead connections
            for dc in disconnected_clients:
                self.disconnect(conversation_id, dc)