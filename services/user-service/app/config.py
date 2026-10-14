"""Configuration du User Service.

Charge les variables d'environnement via pydantic-settings
et expose un singleton `settings` utilisé dans toute l'application.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres de configuration du service utilisateur."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- PostgreSQL individuel ---
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "cube_users"
    POSTGRES_USER: str = "cube"
    POSTGRES_PASSWORD: str = "changeme"

    # --- URL globale (générée automatiquement si absente) ---
    DATABASE_URL: str = ""

    def model_post_init(self, __context) -> None:
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

    # --- JWT / Authentification ---
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://cube.local",
    ]

    # --- Service ---
    SERVICE_NAME: str = "user-service"
    SERVICE_PORT: int = 8001
    DEBUG: bool = False

    # --- gRPC ---
    GRPC_PORT: int = 50051


# Singleton de configuration
settings = Settings()
