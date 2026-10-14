"""Service métier pour le calcul des statistiques et la progression.

Conforme aux règles d'architecture (Règle 1: pas de code métier dans la couche web,
Règle 2: journalisation structurée avec logger, calculs encapsulés).
"""

import logging
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stats import SolveTime, Achievement
from app.schemas.stats import SolveTimeCreate, SolveTimeResponse, StatsResponse, AchievementResponse

logger = logging.getLogger(__name__)


class StatsService:
    """Service encapsulant le calcul des moyennes et l'attribution des succès."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_stats(self, user_id: UUID) -> StatsResponse:
        """Calcule les statistiques d'un utilisateur (PB, AO5, AO12, total)."""
        logger.info("Computing speedcubing stats for user_id=%s", user_id)

        # 1. Total solves
        total_stmt = select(func.count(SolveTime.id)).where(SolveTime.user_id == user_id)
        total_res = await self.db.execute(total_stmt)
        total_solves = total_res.scalar_one() or 0

        if total_solves == 0:
            return StatsResponse(total_solves=0)

        # 2. Personal Best (PB)
        pb_stmt = select(func.min(SolveTime.time_ms)).where(SolveTime.user_id == user_id)
        pb_res = await self.db.execute(pb_stmt)
        personal_best = pb_res.scalar_one()

        # 3. Derniers temps pour moyennes glissantes
        recent_stmt = (
            select(SolveTime.time_ms)
            .where(SolveTime.user_id == user_id)
            .order_by(SolveTime.created_at.desc())
            .limit(100)
        )
        recent_res = await self.db.execute(recent_stmt)
        recent_times = [row[0] for row in recent_res.fetchall()]

        ao5 = self._compute_trimmed_average(recent_times[:5]) if len(recent_times) >= 5 else None
        ao12 = self._compute_trimmed_average(recent_times[:12]) if len(recent_times) >= 12 else None
        ao100 = self._compute_trimmed_average(recent_times[:100]) if len(recent_times) >= 100 else None

        return StatsResponse(
            personal_best=personal_best,
            ao5=ao5,
            ao12=ao12,
            ao100=ao100,
            total_solves=total_solves,
        )

    async def record_solve(self, user_id: UUID, solve_data: SolveTimeCreate) -> SolveTimeResponse:
        """Enregistre un temps de résolution et vérifie l'attribution d'achievements."""
        logger.info("Recording solve for user_id=%s time_ms=%d", user_id, solve_data.time_ms)

        solve = SolveTime(
            user_id=user_id,
            time_ms=solve_data.time_ms,
            scramble=solve_data.scramble,
            puzzle_type=solve_data.puzzle_type,
            penalty=solve_data.penalty,
        )
        self.db.add(solve)
        await self.db.commit()
        await self.db.refresh(solve)

        # Vérifier si c'est son premier solve -> Achievement 'First Solve'
        count_stmt = select(func.count(SolveTime.id)).where(SolveTime.user_id == user_id)
        count_res = await self.db.execute(count_stmt)
        total = count_res.scalar_one() or 0

        if total == 1:
            await self._unlock_achievement(
                user_id,
                name="first_solve",
                description="A réalisé son tout premier solve !",
                icon="trophy",
            )

        # Sub-20 achievement (temps < 20 secondes)
        if solve_data.time_ms < 20000:
            await self._unlock_achievement(
                user_id,
                name="sub_20",
                description="A franchi la barre des 20 secondes !",
                icon="lightning",
            )

        return SolveTimeResponse.model_validate(solve)

    async def get_user_achievements(self, user_id: UUID) -> list[AchievementResponse]:
        """Récupère tous les succès débloqués."""
        stmt = (
            select(Achievement)
            .where(Achievement.user_id == user_id)
            .order_by(Achievement.unlocked_at.desc())
        )
        res = await self.db.execute(stmt)
        achievements = res.scalars().all()
        return [AchievementResponse.model_validate(a) for a in achievements]

    async def _unlock_achievement(self, user_id: UUID, name: str, description: str, icon: str):
        """Débloque un succès s'il n'est pas déjà présent."""
        existing = await self.db.execute(
            select(Achievement).where(Achievement.user_id == user_id, Achievement.name == name)
        )
        if not existing.scalar_one_or_none():
            ach = Achievement(user_id=user_id, name=name, description=description, icon=icon)
            self.db.add(ach)
            await self.db.commit()
            logger.info("Achievement unlocked for user_id=%s: %s", user_id, name)

    @staticmethod
    def _compute_trimmed_average(times: list[int]) -> float:
        """Calcule la moyenne tronquée officielle WCA (en retirant le meilleur et le pire)."""
        if len(times) < 3:
            return round(sum(times) / len(times), 2)
        sorted_times = sorted(times)
        trimmed = sorted_times[1:-1]
        return round(sum(trimmed) / len(trimmed), 2)

