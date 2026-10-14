"""Routeur principal de l'API.

Agrège les sous-routeurs versionnés (v1) et les expose
sous un préfixe commun pour le service utilisateur.
"""
from fastapi import APIRouter
from app.api.v1 import auth, users, stats

api_router = APIRouter()

# --- Routes d'authentification ---
api_router.include_router(
    auth.router,
    prefix="/v1/auth",
    tags=["Authentification"],
)

# --- Routes utilisateurs ---
api_router.include_router(
    users.router,
    prefix="/v1/users",
    tags=["Utilisateurs"],
)

# --- Routes statistiques ---
api_router.include_router(
    stats.router,
    prefix="/v1/stats",
    tags=["Statistiques"],
)
