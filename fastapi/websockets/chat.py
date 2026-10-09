from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

router = APIRouter()

class ChatConnectionManager:
    def __init__(self):
        # Maps ticket_id to connected users (customer and support agent)
        self.active_chats: Dict[str, List[WebSocket]] = {}

    async def connect(self, ws: WebSocket, ticket_id: str):
        await ws.accept()
        if ticket_id not in self.active_chats:
            self.active_chats[ticket_id] = []
        self.active_chats[ticket_id].append(ws)

    def disconnect(self, ws: WebSocket, ticket_id: str):
        if ticket_id in self.active_chats:
            if ws in self.active_chats[ticket_id]:
                self.active_chats[ticket_id].remove(ws)
            if not self.active_chats[ticket_id]:
                del self.active_chats[ticket_id]

    async def broadcast_message(self, ticket_id: str, sender_id: str, message: str, is_agent: bool):
        websockets = self.active_chats.get(ticket_id, [])
        for ws in websockets:
            await ws.send_json({
                "type": "NEW_MESSAGE",
                "data": {
                    "sender_id": sender_id,
                    "message": message,
                    "is_agent": is_agent
                }
            })

manager = ChatConnectionManager()

@router.websocket("/{ticket_id}")
async def chat_endpoint(websocket: WebSocket, ticket_id: str):
    await manager.connect(websocket, ticket_id)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            # Broadcast the typed message to everyone else in the room
            await manager.broadcast_message(
                ticket_id=ticket_id,
                sender_id=payload.get('sender_id'),
                message=payload.get('message'),
                is_agent=payload.get('is_agent', False)
            )
            
            # Note: Also persist to Django `SupportMessage` DB asynchronously
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, ticket_id)
