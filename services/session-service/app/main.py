"""Session & Matchmaking Service - Point d'entrée FastAPI.

Ce microservice gère les sessions de chronométrage solo, la file de
matchmaking basée sur Redis, et les duels 1v1 en temps réel via WebSocket.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import get_redis_client, close_redis
from app.api.router import api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cycle de vie : vérifie la connexion Redis et nettoie à l'arrêt."""
    try:
        redis = await get_redis_client()
        await redis.ping()
        logger.info("Connecté à Redis")
    except Exception as e:
        logger.warning("Avertissement Redis (serveur non démarré en local ?): %s", e)
    yield
    await close_redis()
    logger.info("Connexion Redis fermée")


app = FastAPI(
    title="Cube - Session & Matchmaking Service",
    description="Microservice pour les sessions solo, duels en ligne et WebSocket",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/api/sessions",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Vérification de l'état de santé du service pour Kubernetes."""
    return {"status": "healthy", "service": "session-service"}


class ConnectionManager:
    """Gestionnaire de connexions WebSocket pour les duels en temps réel."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)


ws_manager = ConnectionManager()


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Canal WebSocket pour échanger les temps en direct pendant un duel."""
    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Diffuse ou réagit aux événements de match
            await ws_manager.send_personal_message(
                {"event": "echo", "data": data}, user_id
            )
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id)
