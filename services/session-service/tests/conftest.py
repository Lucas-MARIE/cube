"""Fixtures Pytest pour le Session Service."""

import pytest
import fakeredis.aioredis
from httpx import AsyncClient, ASGITransport

from app.main import app
import app.db.database as db_module


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def mock_redis(monkeypatch):
    """Remplace le client Redis réel par un client simulé en mémoire (fakeredis)."""
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async def fake_get_redis_client():
        return fake

    monkeypatch.setattr(db_module, "get_redis_client", fake_get_redis_client)
    yield fake
    await fake.flushall()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

