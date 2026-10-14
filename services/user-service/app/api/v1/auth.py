"""Endpoints d'authentification.

Gère l'inscription, la connexion et le rafraîchissement
des tokens JWT pour l'authentification des utilisateurs.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Fournisseur de dépendance pour AuthService (permet le mocking sous Pytest)."""
    return AuthService(db)


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Fournisseur de dépendance pour UserService."""
    return UserService(db)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Inscrire un nouvel utilisateur."""
    logger.info("Registering user: %s (%s)", user_data.username, user_data.email)

    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        logger.error("Registration failed: email already taken (%s)", user_data.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte avec cet email existe déjà",
        )

    existing_username = await user_service.get_user_by_username(user_data.username)
    if existing_username:
        logger.error("Registration failed: username already taken (%s)", user_data.username)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur est déjà pris",
        )

    user = await user_service.create_user(user_data)
    logger.info("User registered successfully: id=%s", user.id)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """Authentifier un utilisateur et retourner un token JWT."""
    logger.info("Login attempt for email: %s", credentials.email)
    user = await auth_service.authenticate_user(credentials.email, credentials.password)
    if not user:
        logger.error("Authentication failed for email: %s", credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(subject=str(user.id))
    refresh_token = auth_service.create_refresh_token(subject=str(user.id))

    logger.info("User authenticated: id=%s", user.id)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """Rafraîchir un token d'accès expiré."""
    payload = auth_service.verify_token(refresh_token)
    if not payload:
        logger.error("Invalid or expired refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de rafraîchissement invalide ou expiré",
        )

    user_id: str | None = payload.get("sub")
    if not user_id:
        logger.error("Refresh token missing subject")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide : sujet manquant",
        )

    new_access_token = auth_service.create_access_token(subject=user_id)
    new_refresh_token = auth_service.create_refresh_token(subject=user_id)

    logger.info("Token refreshed for user_id=%s", user_id)
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )
