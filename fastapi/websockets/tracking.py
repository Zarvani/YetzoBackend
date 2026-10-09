from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

router = APIRouter()

class TrackingConnectionManager:
    def __init__(self):
        # Maps booking_id to a list of connected client websockets (e.g. the customer)
        self.active_trackers: Dict[str, List[WebSocket]] = {}

    async def connect(self, ws: WebSocket, booking_id: str):
        await ws.accept()
        if booking_id not in self.active_trackers:
            self.active_trackers[booking_id] = []
        self.active_trackers[booking_id].append(ws)

    def disconnect(self, ws: WebSocket, booking_id: str):
        if booking_id in self.active_trackers:
            if ws in self.active_trackers[booking_id]:
                self.active_trackers[booking_id].remove(ws)
            if not self.active_trackers[booking_id]:
                del self.active_trackers[booking_id]

    async def broadcast_location(self, booking_id: str, lat: float, lng: float):
        """Pushes professional's GPS coordinates to the customer"""
        websockets = self.active_trackers.get(booking_id, [])
        for ws in websockets:
            await ws.send_json({
                "type": "LOCATION_UPDATE", 
                "data": {"lat": lat, "lng": lng}
            })

manager = TrackingConnectionManager()

@router.websocket("/{booking_id}")
async def tracking_endpoint(websocket: WebSocket, booking_id: str):
    """
    Customer connects here to watch the professional's live location.
    The professional's app sends REST or WS updates, which trigger `broadcast_location`.
    """
    await manager.connect(websocket, booking_id)
    try:
        while True:
            # Customer might send "ETA_REQUEST"
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, booking_id)
