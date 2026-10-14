"""Routeur central de l'API Learning Service."""

from fastapi import APIRouter
from app.api.v1.lessons import router as lessons_router
from app.api.v1.algorithms import router as algorithms_router
from app.api.v1.scrambles import router as scrambles_router

api_router = APIRouter()

api_router.include_router(lessons_router, prefix="/lessons", tags=["Lessons"])
api_router.include_router(algorithms_router, prefix="/algorithms", tags=["Algorithms"])
api_router.include_router(scrambles_router, prefix="/scrambles", tags=["Scrambles"])

