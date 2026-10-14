"""Endpoints pour le Matchmaking et les Duels multijoueurs."""

from fastapi import APIRouter
from app.services.matchmaking_service import MatchmakingService
from app.schemas.match import JoinMatchmakingRequest, MatchmakingStatusResponse

router = APIRouter()


@router.post("/join", response_model=MatchmakingStatusResponse)
async def join_matchmaking(data: JoinMatchmakingRequest):
    """Rejoint la file de matchmaking ou associe directement avec un adversaire compatible."""
    scramble_placeholder = "R U R' U' D R2 U' L D2 R B2 D2 R' F2 R2 D2 B2 U2"
    status_str, duel = await MatchmakingService.join_or_find_match(
        user_id=data.user_id,
        username=data.username,
        rating=data.rating,
        scramble=scramble_placeholder,
    )

    if status_str == "matched" and duel:
        return MatchmakingStatusResponse(
            status="matched",
            message="Adversaire trouvé ! Le duel va commencer.",
            match_id=duel.match_id,
            scramble=duel.scramble,
        )

    return MatchmakingStatusResponse(
        status="queued",
        message="En attente d'un adversaire au niveau équivalent...",
    )


@router.delete("/leave")
async def leave_matchmaking(user_id: str, rating: int = 1200):
    """Quitte la file de matchmaking."""
    await MatchmakingService.leave_queue(user_id, rating)
    return {"message": "Retiré de la file d'attente"}

