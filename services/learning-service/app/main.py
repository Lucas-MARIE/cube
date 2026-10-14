"""Learning & Content Service - Point d'entrée FastAPI.

Ce microservice gère le contenu pédagogique, les fiches d'algorithmes
(F2L, OLL, PLL) et la génération de mélanges (scrambles).
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import init_db, close_db
from app.api.router import api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cycle de vie de l'application : connexion MongoDB au démarrage."""
    try:
        await init_db()
        logger.info("Connecté à MongoDB avec Beanie")
    except Exception as e:
        logger.warning("Avertissement BDD (MongoDB non connecté en local ?): %s", e)
    yield
    await close_db()
    logger.info("Connexion MongoDB fermée")


app = FastAPI(
    title="Cube - Learning & Content Service",
    description="Microservice fournissant les leçons, algorithmes et scrambles",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/api/lessons",
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
    return {"status": "healthy", "service": "learning-service"}
