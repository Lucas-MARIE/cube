"""Endpoints pour les sessions de chronomètre solo."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.timer_service import TimerService
from app.schemas.session import (
    StartSessionRequest,
    SessionResponse,
    EndSessionRequest,
    SolveResultResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def get_timer_service() -> TimerService:
    """Fournisseur de dépendance pour TimerService (permet le mocking en test)."""
    return TimerService()


@router.post("/start", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_solo_session(
    data: StartSessionRequest,
    timer_service: TimerService = Depends(get_timer_service),
):
    """Démarre une nouvelle session de résolution avec son scramble associé."""
    logger.info("Starting solo session for user=%s", data.user_id)
    session = await timer_service.create_session(data.user_id, data.scramble)
    return SessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        scramble=session.scramble,
        started_at=session.started_at,
    )


@router.post("/end", response_model=SolveResultResponse)
async def end_solo_session(
    data: EndSessionRequest,
    timer_service: TimerService = Depends(get_timer_service),
):
    """Enregistre le temps final d'une session de résolution."""
    logger.info("Ending session=%s with time_ms=%d", data.session_id, data.solve_time_ms)
    session = await timer_service.complete_session(data.session_id, data.solve_time_ms)
    if not session:
        logger.error("Session not found or expired: %s", data.session_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session introuvable ou expirée.",
        )

    return SolveResultResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        solve_time_ms=session.solve_time_ms or data.solve_time_ms,
        scramble=session.scramble,
        message="Temps enregistré avec succès.",
    )
