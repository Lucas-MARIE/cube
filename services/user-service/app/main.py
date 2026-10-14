"""User & Progression Service - Point d'entrée FastAPI.

Ce service gère l'authentification, les profils utilisateurs,
et le suivi des statistiques de speedcubing.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router
from app.db.database import engine, Base

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application.

    - Au démarrage : se connecte à PostgreSQL avec retries et crée les tables (dev)
    - À l'arrêt : ferme les connexions du pool
    """
    logger.info("Démarrage de user-service sur %s...", settings.DATABASE_URL.split("@")[-1])
    connected = False
    for attempt in range(1, 6):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Connexion PostgreSQL réussie et tables synchronisées.")
            connected = True
            break
        except Exception as e:
            logger.warning("Tentative %d/5 : PostgreSQL non prêt (%s), nouvelle tentative dans 2s...", attempt, e)
            await asyncio.sleep(2)

    if not connected:
        logger.error("Impossible d'initialiser la base de données PostgreSQL après 5 tentatives.")

    yield
    # Shutdown: dispose engine
    await engine.dispose()
    logger.info("Pool PostgreSQL fermé proprement.")


app = FastAPI(
    title="Cube - User Service",
    description="Service de gestion des utilisateurs et de la progression",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/api/users",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Endpoint de santé pour Kubernetes et Docker Compose liveness/readiness probes."""
    return {"status": "healthy", "service": "user-service"}
