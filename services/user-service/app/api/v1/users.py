"""Endpoints CRUD pour la gestion des utilisateurs.

Fournit les opérations de lecture, mise à jour et suppression
du profil utilisateur authentifié.
"""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.services.auth_service import get_current_user
from app.services.user_service import UserService
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Fournisseur de dépendance pour UserService (permet le mocking sous Pytest)."""
    return UserService(db)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Récupérer le profil de l'utilisateur connecté."""
    logger.info("GET /users/me for user_id=%s", current_user.id)
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Récupérer le profil public d'un utilisateur par son ID."""
    logger.info("GET /users/%s", user_id)
    user = await service.get_user(user_id)
    if not user:
        logger.error("User not found: %s", user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Mettre à jour le profil de l'utilisateur connecté."""
    logger.info("PUT /users/me for user_id=%s", current_user.id)
    updated_user = await service.update_user(current_user.id, update_data)
    return UserResponse.model_validate(updated_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    """Supprimer le compte de l'utilisateur connecté."""
    logger.info("DELETE /users/me for user_id=%s", current_user.id)
    await service.delete_user(current_user.id)
