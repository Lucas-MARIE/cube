"""Modèle SQLAlchemy pour la table User.

Représente un utilisateur de la plateforme Cube.com
avec ses informations de profil et d'authentification.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    """Table des utilisateurs.

    Stocke les informations de profil et les identifiants
    pour l'authentification par mot de passe hashé.

    Attributes:
        id: Identifiant unique UUID généré automatiquement.
        username: Nom d'utilisateur unique (max 50 caractères).
        email: Adresse email unique pour l'authentification.
        hashed_password: Mot de passe hashé avec bcrypt.
        avatar_url: URL optionnelle de l'avatar du profil.
        created_at: Date de création du compte (UTC).
        updated_at: Date de dernière mise à jour (UTC).
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relations
    solve_times: Mapped[list["SolveTime"]] = relationship(
        "SolveTime",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    achievements: Mapped[list["Achievement"]] = relationship(
        "Achievement",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Représentation textuelle de l'utilisateur."""
        return f"<User(id={self.id}, username={self.username!r})>"
