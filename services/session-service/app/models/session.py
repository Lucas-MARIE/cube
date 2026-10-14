"""Modèles de données pour les sessions de résolution."""

from datetime import datetime
from pydantic import BaseModel, Field


class SoloSession(BaseModel):
    """Session de résolution solo."""

    session_id: str
    user_id: str
    scramble: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed: bool = False
    solve_time_ms: int | None = None

