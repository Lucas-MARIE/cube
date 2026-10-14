"""Endpoints de statistiques et progression.

Gère l'enregistrement des temps de résolution,
le calcul des moyennes et le suivi des succès (achievements).
"""
import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.schemas.stats import (
    AchievementResponse,
    SolveTimeCreate,
    SolveTimeResponse,
    StatsResponse,
)
from app.services.auth_service import get_current_user
from app.services.stats_service import StatsService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_stats_service(db: AsyncSession = Depends(get_db)) -> StatsService:
    """Fournisseur de dépendance pour StatsService (permet le mocking en test)."""
    return StatsService(db)


@router.get("/me/stats", response_model=StatsResponse)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    stats_service: StatsService = Depends(get_stats_service),
) -> StatsResponse:
    """Récupérer les statistiques de l'utilisateur connecté."""
    logger.info("GET /me/stats for user=%s", current_user.id)
    return await stats_service.get_user_stats(current_user.id)


@router.post("/me/solves", response_model=SolveTimeResponse, status_code=status.HTTP_201_CREATED)
async def record_solve(
    solve_data: SolveTimeCreate,
    current_user: User = Depends(get_current_user),
    stats_service: StatsService = Depends(get_stats_service),
) -> SolveTimeResponse:
    """Enregistrer un nouveau temps de résolution."""
    logger.info("POST /me/solves for user=%s (time=%d ms)", current_user.id, solve_data.time_ms)
    return await stats_service.record_solve(current_user.id, solve_data)


@router.get("/me/achievements", response_model=list[AchievementResponse])
async def get_my_achievements(
    current_user: User = Depends(get_current_user),
    stats_service: StatsService = Depends(get_stats_service),
) -> list[AchievementResponse]:
    """Récupérer la liste des succès débloqués par l'utilisateur."""
    logger.info("GET /me/achievements for user=%s", current_user.id)
    return await stats_service.get_user_achievements(current_user.id)
