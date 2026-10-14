"""Connexion asynchrone à MongoDB via Motor et initialisation de Beanie."""

import motor.motor_asyncio
from beanie import init_beanie

from app.config import settings
from app.models.lesson import Lesson
from app.models.algorithm import Algorithm

client: motor.motor_asyncio.AsyncIOMotorClient | None = None


async def init_db():
    """Initialise le client MongoDB et mappe les documents Beanie."""
    global client
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    database = client[settings.MONGO_DB]
    await init_beanie(
        database=database,
        document_models=[
            Lesson,
            Algorithm,
        ],
    )


async def close_db():
    """Ferme proprement le client MongoDB."""
    global client
    if client:
        client.close()

