"""Configuration du service Session & Matchmaking via Pydantic Settings."""

import json
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration générale du Session Service."""

    PORT: int = 8003
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = "development"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    # gRPC connection vers user-service
    USER_SERVICE_GRPC_HOST: str = "user-service"
    USER_SERVICE_GRPC_PORT: int = 50051

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
    def REDIS_URL(self) -> str:
        """Construit l'URL de connexion Redis."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

