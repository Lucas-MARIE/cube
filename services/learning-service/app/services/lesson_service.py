"""Logique métier pour la gestion des leçons et des algorithmes."""

from app.models.lesson import Lesson
from app.models.algorithm import Algorithm
from app.schemas.lesson import LessonCreate
from app.schemas.algorithm import AlgorithmCreate


class LessonService:
    """Service de gestion du contenu pédagogique."""

    @staticmethod
    async def get_all_lessons(category: str | None = None) -> list[Lesson]:
        query = {}
        if category:
            query["category"] = category.lower()
        return await Lesson.find(query).sort("+order").to_list()

    @staticmethod
    async def get_lesson_by_id(lesson_id: str) -> Lesson | None:
        return await Lesson.get(lesson_id)

    @staticmethod
    async def create_lesson(data: LessonCreate) -> Lesson:
        lesson = Lesson(**data.model_dump())
        await lesson.insert()
        return lesson

    @staticmethod
    async def get_all_algorithms(category: str | None = None) -> list[Algorithm]:
        query = {}
        if category and category != "ALL":
            query["category"] = category.upper()
        return await Algorithm.find(query).sort("+name").to_list()

    @staticmethod
    async def create_algorithm(data: AlgorithmCreate) -> Algorithm:
        algo = Algorithm(**data.model_dump())
        await algo.insert()
        return algo

