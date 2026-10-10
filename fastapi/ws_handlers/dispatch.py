from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json

router = APIRouter()

class DispatchConnectionManager:
    def __init__(self):
        # Maps professional_id to their active websocket connection
        self.active_professionals: Dict[str, WebSocket] = {}

    async def connect(self, ws: WebSocket, professional_id: str):
        await ws.accept()
        self.active_professionals[professional_id] = ws
        print(f"Professional {professional_id} connected to dispatch.")

    def disconnect(self, professional_id: str):
        if professional_id in self.active_professionals:
            del self.active_professionals[professional_id]
            print(f"Professional {professional_id} disconnected from dispatch.")

    async def broadcast_job(self, professional_id: str, job_data: dict):
        """Called by Celery/Redis pub-sub when a new booking is assigned/broadcasted"""
        ws = self.active_professionals.get(professional_id)
        if ws:
            await ws.send_json({"type": "NEW_JOB", "data": job_data})
            return True
        return False

manager = DispatchConnectionManager()

@router.websocket("/{professional_id}")
async def dispatch_endpoint(websocket: WebSocket, professional_id: str):
    await manager.connect(websocket, professional_id)
    try:
        while True:
            # Listen for job acceptance/rejection from the professional's app
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            # Here we would typically forward this back to Django via REST or Redis pubsub
            # e.g., if payload['action'] == 'ACCEPT_JOB':
            
    except WebSocketDisconnect:
        manager.disconnect(professional_id)
