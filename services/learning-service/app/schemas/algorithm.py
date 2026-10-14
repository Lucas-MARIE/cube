"""Schemas Pydantic pour les Algorithmes."""

from datetime import datetime
from pydantic import BaseModel, Field


class AlgorithmCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str
    notation: str
    description: str = ""
    triggers: list[str] = []
    image_url: str | None = None


class AlgorithmResponse(BaseModel):
    id: str
    name: str
    category: str
    notation: str
    description: str
    triggers: list[str]
    image_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScrambleResponse(BaseModel):
    scramble: str
    length: int
    case: str | None = None

