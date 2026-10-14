"""Schémas Pydantic pour les utilisateurs et l'authentification.

Définit les modèles de validation pour les requêtes et réponses
liées aux opérations utilisateur et aux tokens JWT.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    """Schéma de création d'un nouvel utilisateur.

    Utilisé lors de l'inscription pour valider les données saisies.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Nom d'utilisateur unique (lettres, chiffres, - et _)",
        examples=["speedcuber42"],
    )
    email: EmailStr = Field(
        ...,
        description="Adresse email valide",
        examples=["cuber@cube.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Mot de passe (8 caractères minimum)",
        examples=["SecureP@ss123"],
    )


class UserLogin(BaseModel):
    """Schéma d'authentification par email et mot de passe."""

    email: EmailStr = Field(
        ...,
        description="Adresse email du compte",
        examples=["cuber@cube.com"],
    )
    password: str = Field(
        ...,
        description="Mot de passe du compte",
        examples=["SecureP@ss123"],
    )


class UserUpdate(BaseModel):
    """Schéma de mise à jour partielle du profil utilisateur.

    Tous les champs sont optionnels : seuls les champs fournis
    seront mis à jour.
    """

    username: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Nouveau nom d'utilisateur",
    )
    email: EmailStr | None = Field(
        None,
        description="Nouvelle adresse email",
    )
    avatar_url: str | None = Field(
        None,
        max_length=500,
        description="URL de l'avatar de profil",
    )


class UserResponse(BaseModel):
    """Schéma de réponse pour les données utilisateur.

    Exclut le mot de passe hashé pour la sécurité.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: EmailStr
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """Schéma de réponse pour les tokens JWT.

    Contient la paire access_token / refresh_token
    nécessaire à l'authentification.
    """

    access_token: str = Field(..., description="Token d'accès JWT")
    refresh_token: str = Field(..., description="Token de rafraîchissement JWT")
    token_type: str = Field(default="bearer", description="Type de token")


class TokenPayload(BaseModel):
    """Schéma du payload décodé d'un token JWT.

    Utilisé en interne pour extraire les informations
    du token après vérification de sa signature.
    """

    sub: str = Field(..., description="Sujet du token (user_id)")
    exp: int = Field(..., description="Timestamp d'expiration")
    type: str = Field(default="access", description="Type de token (access/refresh)")
