"""Configuration du User Service.

Charge les variables d'environnement via pydantic-settings
et expose un singleton `settings` utilisé dans toute l'application.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres de configuration du service utilisateur.

    Toutes les valeurs peuvent être surchargées via des variables
    d'environnement ou un fichier `.env`.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Base de données ---
    DATABASE_URL: str = "postgresql+asyncpg://cube_user:cube_password@localhost:5432/cube_users"

    # --- JWT / Authentification ---
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # --- Service ---
    SERVICE_NAME: str = "user-service"
    SERVICE_PORT: int = 8001
    DEBUG: bool = False

    # --- gRPC ---
    GRPC_PORT: int = 50051


# Singleton de configuration
settings = Settings()
