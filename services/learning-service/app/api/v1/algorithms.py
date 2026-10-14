"""Endpoints pour la banque d'algorithmes Rubik's Cube (CFOP)."""

from fastapi import APIRouter, status
from app.services.lesson_service import LessonService
from app.schemas.algorithm import AlgorithmCreate, AlgorithmResponse

router = APIRouter()


@router.get("", response_model=list[AlgorithmResponse])
async def list_algorithms(category: str | None = None):
    """Liste les algorithmes disponibles (filtre par F2L, OLL, PLL)."""
    algos = await LessonService.get_all_algorithms(category)
    return [
        AlgorithmResponse(
            id=str(a.id),
            name=a.name,
            category=a.category,
            notation=a.notation,
            description=a.description,
            triggers=a.triggers,
            image_url=a.image_url,
            created_at=a.created_at,
        )
        for a in algos
    ]


@router.post("", response_model=AlgorithmResponse, status_code=status.HTTP_201_CREATED)
async def create_algorithm(data: AlgorithmCreate):
    """Ajoute une formule d'algorithme dans la base de données."""
    algo = await LessonService.create_algorithm(data)
    return AlgorithmResponse(
        id=str(algo.id),
        name=algo.name,
        category=algo.category,
        notation=algo.notation,
        description=algo.description,
        triggers=algo.triggers,
        image_url=algo.image_url,
        created_at=algo.created_at,
    )

