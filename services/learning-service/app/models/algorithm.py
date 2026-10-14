"""Modèle Beanie/MongoDB pour les Algorithmes de Rubik's Cube."""

from datetime import datetime
from beanie import Document
from pydantic import Field


class Algorithm(Document):
    """Document représentant une formule d'algorithme (F2L, OLL, PLL)."""

    name: str = Field(..., max_length=100)
    category: str = Field(..., description="F2L, OLL, PLL, CROSS")
    notation: str = Field(..., description="Séquence de mouvements standards (ex: R U R' U')")
    description: str = ""
    triggers: list[str] = Field(default_factory=list, description="Indicateurs de reconnaissance visuelle")
    image_url: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "algorithms"
        indexes = [
            "category",
            "name",
        ]

