"""Schemas Pydantic pour les requêtes/réponses de session."""

from datetime import datetime
from pydantic import BaseModel, Field


class StartSessionRequest(BaseModel):
    user_id: str
    scramble: str


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    scramble: str
    started_at: datetime


class EndSessionRequest(BaseModel):
    session_id: str
    solve_time_ms: int = Field(..., gt=0, description="Temps en millisecondes")


class SolveResultResponse(BaseModel):
    session_id: str
    user_id: str
    solve_time_ms: int
    scramble: str
    is_personal_best: bool = False
    message: str = "Solve enregistré avec succès"

