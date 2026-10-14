"""Schemas Pydantic pour le matchmaking et les duels."""

from pydantic import BaseModel, Field


class JoinMatchmakingRequest(BaseModel):
    user_id: str
    username: str
    rating: int = Field(default=1200, ge=0)
    game_mode: str = "ranked"


class MatchmakingStatusResponse(BaseModel):
    status: str  # "queued", "matched"
    message: str
    match_id: str | None = None
    opponent_username: str | None = None
    scramble: str | None = None


class SubmitDuelTimeRequest(BaseModel):
    match_id: str
    user_id: str
    solve_time_ms: int

