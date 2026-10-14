"""Connexion asynchrone à Redis pour le stockage des sessions et matchmaking."""

import redis.asyncio as redis
from app.config import settings

redis_pool: redis.ConnectionPool | None = None


async def get_redis_client() -> redis.Redis:
    """Retourne une instance de client Redis asynchrone depuis le pool."""
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20,
        )
    return redis.Redis(connection_pool=redis_pool)


async def close_redis():
    """Ferme le pool de connexions Redis."""
    global redis_pool
    if redis_pool:
        await redis_pool.disconnect()

