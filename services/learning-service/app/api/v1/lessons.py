"""Endpoints pour la gestion des Leçons."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.lesson_service import LessonService
from app.schemas.lesson import LessonCreate, LessonResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def get_lesson_service() -> LessonService:
    """Fournisseur de dépendance pour LessonService."""
    return LessonService()


@router.get("", response_model=list[LessonResponse])
async def list_lessons(
    category: str | None = None,
    service: LessonService = Depends(get_lesson_service),
):
    """Liste l'ensemble des leçons disponibles avec filtre optionnel."""
    logger.info("Listing lessons (category=%s)", category)
    lessons = await service.get_all_lessons(category)
    return [
        LessonResponse(
            id=str(l.id),
            title=l.title,
            category=l.category,
            difficulty=l.difficulty,
            description=l.description,
            steps=l.steps,
            video_url=l.video_url,
            order=l.order,
            created_at=l.created_at,
        )
        for l in lessons
    ]


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: str,
    service: LessonService = Depends(get_lesson_service),
):
    """Récupère le détail complet d'une leçon par son identifiant."""
    logger.info("Fetching lesson id=%s", lesson_id)
    lesson = await service.get_lesson_by_id(lesson_id)
    if not lesson:
        logger.error("Lesson not found: %s", lesson_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leçon introuvable.",
        )
    return LessonResponse(
        id=str(lesson.id),
        title=lesson.title,
        category=lesson.category,
        difficulty=lesson.difficulty,
        description=lesson.description,
        steps=lesson.steps,
        video_url=lesson.video_url,
        order=lesson.order,
        created_at=lesson.created_at,
    )


@router.post("", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    data: LessonCreate,
    service: LessonService = Depends(get_lesson_service),
):
    """Crée une nouvelle leçon pédagogique."""
    logger.info("Creating new lesson: %s", data.title)
    lesson = await service.create_lesson(data)
    return LessonResponse(
        id=str(lesson.id),
        title=lesson.title,
        category=lesson.category,
        difficulty=lesson.difficulty,
        description=lesson.description,
        steps=lesson.steps,
        video_url=lesson.video_url,
        order=lesson.order,
        created_at=lesson.created_at,
    )
