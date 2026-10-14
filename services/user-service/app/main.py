"""User & Progression Service - Point d'entrée FastAPI.

Ce service gère l'authentification, les profils utilisateurs,
et le suivi des statistiques de speedcubing.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.router import api_router
from app.db.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application.
    
    - Au démarrage : crée les tables en BDD (dev only)
    - À l'arrêt : ferme les connexions
    """
    # Startup: create tables (in dev; use Alembic migrations in prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


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
    """Endpoint de santé pour Kubernetes liveness/readiness probes."""
    return {"status": "healthy", "service": "user-service"}
