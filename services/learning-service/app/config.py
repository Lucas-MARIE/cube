"""Configuration du service Learning & Content via Pydantic Settings."""

import json
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration générale du Learning Service."""

    PORT: int = 8002
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = "development"

    # MongoDB
    MONGO_HOST: str = "mongodb"
    MONGO_PORT: int = 27017
    MONGO_DB: str = "cube_learning"
    MONGO_USER: str | None = None
    MONGO_PASSWORD: str | None = None

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080", "http://cube.local"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except ValueError:
                return [i.strip() for i in v.split(",")]
        return v

    @property
    def MONGO_URI(self) -> str:
        """Construit l'URI de connexion MongoDB."""
        if self.MONGO_USER and self.MONGO_PASSWORD:
            return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}?authSource=admin"
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

