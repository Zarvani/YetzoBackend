from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from websockets.dispatch import router as dispatch_router
from websockets.tracking import router as tracking_router
from websockets.chat import router as chat_router

app = FastAPI(
    title="YETZO Realtime Engine",
    description="High-performance asynchronous microservice for WebSockets (Dispatch, Tracking, Chat)",
    version="1.0.0"
)

# Standard CORS config for the frontend and mobile apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the WebSockets routers
app.include_router(dispatch_router, prefix="/ws/dispatch", tags=["Dispatch"])
app.include_router(tracking_router, prefix="/ws/tracking", tags=["Live Tracking"])
app.include_router(chat_router, prefix="/ws/chat", tags=["Support Chat"])

@app.get("/")
async def root():
    return {
        "service": "Yetzo Realtime Engine",
        "status": "online",
        "endpoints": [
            "/ws/dispatch/{professional_id}",
            "/ws/tracking/{booking_id}",
            "/ws/chat/{ticket_id}"
        ]
    }
