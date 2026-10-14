"""Logique métier pour le chronométrage et l'enregistrement de sessions."""

import json
import uuid
from datetime import datetime
from app.db.database import get_redis_client
from app.models.session import SoloSession


class TimerService:
    """Gestion des sessions de chronométrage dans Redis."""

    SESSION_KEY_PREFIX = "cube:session:"

    @classmethod
    async def create_session(cls, user_id: str, scramble: str) -> SoloSession:
        redis = await get_redis_client()
        session_id = str(uuid.uuid4())
        session = SoloSession(
            session_id=session_id,
            user_id=user_id,
            scramble=scramble,
            started_at=datetime.utcnow(),
        )
        # Expiration après 1 heure si non terminée
        await redis.set(
            f"{cls.SESSION_KEY_PREFIX}{session_id}",
            session.model_dump_json(),
            ex=3600,
        )
        return session

    @classmethod
    async def complete_session(cls, session_id: str, solve_time_ms: int) -> SoloSession | None:
        redis = await get_redis_client()
        key = f"{cls.SESSION_KEY_PREFIX}{session_id}"
        data = await redis.get(key)
        if not data:
            return None

        session_dict = json.loads(data)
        session_dict["completed"] = True
        session_dict["solve_time_ms"] = solve_time_ms

        updated_session = SoloSession(**session_dict)
        # Conserver la session terminée 24h
        await redis.set(key, updated_session.model_dump_json(), ex=86400)
        return updated_session

