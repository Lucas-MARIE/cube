"""Endpoints pour la génération de mélanges (scrambles)."""

from fastapi import APIRouter
from app.services.scramble_service import ScrambleService
from app.schemas.algorithm import ScrambleResponse

router = APIRouter()


@router.get("/random", response_model=ScrambleResponse)
async def get_random_scramble(length: int = 20):
    """Génère un mélange aléatoire officiel de 20 mouvements."""
    scramble = ScrambleService.generate_random_scramble(length=length)
    return ScrambleResponse(scramble=scramble, length=length)


@router.get("/targeted", response_model=ScrambleResponse)
async def get_targeted_scramble(case: str = "t-perm"):
    """Génère un mélange préparant un cas d'entraînement spécifique (ex: t-perm, sune)."""
    res = ScrambleService.get_targeted_scramble(case)
    return ScrambleResponse(
        scramble=res["scramble"],
        length=res["length"],
        case=res["case"],
    )

