"""Service d'authentification JWT.

Gère la création et la vérification des tokens JWT,
ainsi que l'authentification des utilisateurs par
email et mot de passe.
"""
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db
from app.models.user import User
from app.services.user_service import UserService

# Schéma d'authentification Bearer
security = HTTPBearer()


class AuthService:
    """Service d'authentification et de gestion des tokens JWT.

    Fournit les méthodes pour :
    - Authentifier un utilisateur (email + mot de passe)
    - Créer des tokens d'accès et de rafraîchissement
    - Vérifier et décoder des tokens JWT
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialiser le service avec une session de base de données.

        Args:
            db: Session async SQLAlchemy.
        """
        self.db = db
        self.user_service = UserService(db)

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authentifier un utilisateur par email et mot de passe.

        Vérifie que l'email existe en base et que le mot de passe
        correspond au hash stocké.

        Args:
            email: Adresse email de l'utilisateur.
            password: Mot de passe en clair à vérifier.

        Returns:
            L'utilisateur authentifié, ou None si échec.
        """
        user = await self.user_service.get_user_by_email(email)
        if not user:
            return None
        if not self.user_service.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_access_token(subject: str) -> str:
        """Créer un token d'accès JWT.

        Args:
            subject: Identifiant du sujet (user_id).

        Returns:
            Token JWT encodé.
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload: dict[str, Any] = {
            "sub": subject,
            "exp": expire,
            "type": "access",
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def create_refresh_token(subject: str) -> str:
        """Créer un token de rafraîchissement JWT.

        Les refresh tokens ont une durée de vie plus longue
        que les access tokens (définie dans la configuration).

        Args:
            subject: Identifiant du sujet (user_id).

        Returns:
            Token JWT de rafraîchissement encodé.
        """
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        payload: dict[str, Any] = {
            "sub": subject,
            "exp": expire,
            "type": "refresh",
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def verify_token(token: str) -> dict[str, Any] | None:
        """Vérifier et décoder un token JWT.

        Args:
            token: Token JWT à vérifier.

        Returns:
            Le payload décodé, ou None si le token est invalide.
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except JWTError:
            return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dépendance FastAPI pour récupérer l'utilisateur courant.

    Extrait le token JWT du header Authorization, le vérifie,
    et retourne l'utilisateur correspondant depuis la base.

    Args:
        credentials: Credentials HTTP Bearer extraites du header.
        db: Session de base de données injectée.

    Returns:
        L'utilisateur authentifié.

    Raises:
        HTTPException 401: Si le token est invalide ou l'utilisateur n'existe pas.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = AuthService.verify_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    token_type: str | None = payload.get("type")

    if user_id is None or token_type != "access":
        raise credentials_exception

    user_service = UserService(db)
    user = await user_service.get_user(UUID(user_id))
    if user is None:
        raise credentials_exception

    return user
