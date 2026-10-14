"""Schemas Pydantic pour les Leçons."""

from datetime import datetime
from pydantic import BaseModel, Field


class StepSchema(BaseModel):
    title: str
    content: str
    notation: str | None = None
    diagram_url: str | None = None


class LessonCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    category: str
    difficulty: int = Field(default=1, ge=1, le=5)
    description: str
    steps: list[StepSchema] = []
    video_url: str | None = None
    order: int = 0


class LessonResponse(BaseModel):
    id: str
    title: str
    category: str
    difficulty: int
    description: str
    steps: list[StepSchema]
    video_url: str | None
    order: int
    created_at: datetime

    model_config = {"from_attributes": True}

