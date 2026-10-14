"""Service de matchmaking rapide pour les duels 1v1 en temps réel."""

import json
import uuid
from app.db.database import get_redis_client
from app.models.match import MatchDuel


class MatchmakingService:
    """Gestion de la file d'attente et appariement par Elo dans Redis."""

    QUEUE_KEY = "cube:matchmaking:queue"
    MATCH_PREFIX = "cube:match:"

    @classmethod
    async def join_or_find_match(
        cls, user_id: str, username: str, rating: int, scramble: str
    ) -> tuple[str, MatchDuel | None]:
        """Cherche un joueur avec un rating proche (±150) ou place l'utilisateur en file d'attente."""
        redis = await get_redis_client()

        # Chercher des joueurs dans l'intervalle [rating - 150, rating + 150]
        opponents = await redis.zrangebyscore(
            cls.QUEUE_KEY,
            min=max(0, rating - 150),
            max=rating + 150,
            start=0,
            num=2,
        )

        for opp_entry in opponents:
            opp_data = json.loads(opp_entry)
            if opp_data["user_id"] != user_id:
                # Adversaire trouvé ! On le retire de la file
                await redis.zrem(cls.QUEUE_KEY, opp_entry)

                match_id = str(uuid.uuid4())
                duel = MatchDuel(
                    match_id=match_id,
                    player1_id=opp_data["user_id"],
                    player2_id=user_id,
                    scramble=scramble,
                    status="ongoing",
                )
                await redis.set(
                    f"{cls.MATCH_PREFIX}{match_id}",
                    duel.model_dump_json(),
                    ex=1800,
                )
                return "matched", duel

        # Aucun adversaire trouvé immédiatement : on s'enregistre dans le Sorted Set Redis
        player_payload = json.dumps({"user_id": user_id, "username": username, "rating": rating})
        await redis.zadd(cls.QUEUE_KEY, {player_payload: rating})
        return "queued", None

    @classmethod
    async def leave_queue(cls, user_id: str, rating: int):
        redis = await get_redis_client()
        # Retirer toute entrée appartenant à ce user
        entries = await redis.zrangebyscore(cls.QUEUE_KEY, rating, rating)
        for entry in entries:
            data = json.loads(entry)
            if data["user_id"] == user_id:
                await redis.zrem(cls.QUEUE_KEY, entry)

