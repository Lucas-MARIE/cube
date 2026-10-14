"""Routeur principal pour le Session Service."""

from fastapi import APIRouter
from app.api.v1.sessions import router as sessions_router
from app.api.v1.matches import router as matches_router

api_router = APIRouter()

api_router.include_router(sessions_router, prefix="/solo", tags=["Solo Sessions"])
api_router.include_router(matches_router, prefix="/matchmaking", tags=["Matchmaking"])

