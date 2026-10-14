"""Modèle Beanie/MongoDB pour les Leçons de Speedcubing."""

from datetime import datetime
from beanie import Document
from pydantic import Field


class Lesson(Document):
    """Document représentant une leçon d'apprentissage."""

    title: str = Field(..., max_length=150)
    category: str = Field(..., description="beginner, f2l, oll, pll, general")
    difficulty: int = Field(default=1, ge=1, le=5)
    description: str
    steps: list[dict] = Field(default_factory=list, description="Liste ordonnée d'étapes (titre, contenu, notation)")
    video_url: str | None = None
    order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lessons"
        indexes = [
            "category",
            "order",
        ]

