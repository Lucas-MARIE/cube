"""Modèles de données pour les duels en ligne (matchmaking)."""

from datetime import datetime
from pydantic import BaseModel, Field


class MatchDuel(BaseModel):
    """Duel opposant deux cubeurs sur le même scramble."""

    match_id: str
    player1_id: str
    player2_id: str
    scramble: str
    status: str = "pending"  # pending, ongoing, finished, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    player1_time_ms: int | None = None
    player2_time_ms: int | None = None
    winner_id: str | None = None

