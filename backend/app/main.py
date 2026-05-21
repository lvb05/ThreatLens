from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine, SessionLocal
from app.core.websocket_manager import manager
from app.routes import alerts
import asyncio

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ThreatLens API",
    version="1.0.0",
    description="AI-assisted Security Operations Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts.router)

@app.on_event("startup")
async def startup_event():
    from app.services.simulator import run_simulator
    asyncio.create_task(run_simulator(manager, SessionLocal))
    print("[ThreatLens] API started. Simulator running.")

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def root():
    return {"message": "ThreatLens API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}