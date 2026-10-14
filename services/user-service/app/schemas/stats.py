"""Schémas Pydantic pour les statistiques de speedcubing.

Définit les modèles de validation pour les temps de résolution,
les statistiques agrégées et les succès.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class SolveTimeCreate(BaseModel):
    """Schéma d'enregistrement d'un nouveau temps de résolution.

    Envoyé par le client après chaque résolution du cube.
    """

    time_ms: int = Field(
        ...,
        gt=0,
        description="Temps de résolution en millisecondes",
        examples=[12345],
    )
    scramble: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Notation du mélange (ex: R U R' U')",
        examples=["R U R' U' F' U2 L' B D R2 F2 U' L2 D B2 U F2 R2 D L2"],
    )
    puzzle_type: str = Field(
        default="3x3",
        max_length=10,
        description="Type de puzzle (3x3, 2x2, 4x4, etc.)",
        examples=["3x3"],
    )
    penalty: str | None = Field(
        default=None,
        description="Pénalité éventuelle (+2 secondes ou DNF)",
        examples=[None, "+2", "DNF"],
    )


class SolveTimeResponse(BaseModel):
    """Schéma de réponse pour un temps de résolution enregistré."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    time_ms: int
    scramble: str
    puzzle_type: str
    penalty: str | None = None
    created_at: datetime


class StatsResponse(BaseModel):
    """Schéma de réponse pour les statistiques agrégées.

    Contient les indicateurs clés de performance du speedcuber :
    record personnel, moyennes glissantes et compteur total.
    """

    personal_best: int | None = Field(
        None,
        description="Record personnel en millisecondes",
    )
    ao5: float | None = Field(
        None,
        description="Moyenne des 5 derniers temps (Average of 5)",
    )
    ao12: float | None = Field(
        None,
        description="Moyenne des 12 derniers temps (Average of 12)",
    )
    ao100: float | None = Field(
        None,
        description="Moyenne des 100 derniers temps (Average of 100)",
    )
    total_solves: int = Field(
        default=0,
        description="Nombre total de résolutions",
    )
    best_ao5: float | None = Field(
        None,
        description="Meilleure moyenne de 5 historique",
    )
    best_ao12: float | None = Field(
        None,
        description="Meilleure moyenne de 12 historique",
    )


class AchievementResponse(BaseModel):
    """Schéma de réponse pour un succès débloqué."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    icon: str
    unlocked_at: datetime
