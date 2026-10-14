"""Configuration de la base de données PostgreSQL (async).

Met en place le moteur SQLAlchemy asynchrone, la factory
de sessions et la classe de base pour les modèles ORM.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Moteur asynchrone PostgreSQL via asyncpg
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Factory de sessions asynchrones
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Classe de base pour tous les modèles SQLAlchemy.

    Hérite de DeclarativeBase pour bénéficier du système
    de mapping déclaratif moderne de SQLAlchemy 2.0.
    """

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dépendance FastAPI pour obtenir une session de base de données.

    Crée une session async qui est automatiquement fermée
    après le traitement de la requête (via le yield).

    Yields:
        Session async SQLAlchemy prête à l'emploi.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
