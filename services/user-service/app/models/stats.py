"""Modèles SQLAlchemy pour les statistiques de speedcubing.

Contient les tables SolveTime (temps de résolution)
et Achievement (succès débloqués).
"""
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class SolveTime(Base):
    """Table des temps de résolution.

    Enregistre chaque résolution du Rubik's Cube avec
    le temps en millisecondes et le scramble utilisé.

    Attributes:
        id: Identifiant unique UUID.
        user_id: Référence vers l'utilisateur (FK).
        time_ms: Temps de résolution en millisecondes.
        scramble: Notation du mélange utilisé.
        puzzle_type: Type de puzzle (3x3, 2x2, etc.).
        penalty: Pénalité éventuelle (None, '+2', 'DNF').
        created_at: Date d'enregistrement (UTC).
    """

    __tablename__ = "solve_times"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    time_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    scramble: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    puzzle_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="3x3",
    )
    penalty: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relation inverse vers User
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="solve_times",
    )

    def __repr__(self) -> str:
        """Représentation textuelle du temps de résolution."""
        return f"<SolveTime(id={self.id}, time_ms={self.time_ms})>"


class Achievement(Base):
    """Table des succès (achievements).

    Enregistre les accomplissements débloqués par chaque
    utilisateur au fil de sa progression.

    Attributes:
        id: Identifiant unique UUID.
        user_id: Référence vers l'utilisateur (FK).
        name: Nom interne du succès.
        description: Description lisible du succès.
        icon: Nom de l'icône associée.
        unlocked_at: Date de déblocage (UTC).
    """

    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        default="",
    )
    icon: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="trophy",
    )
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relation inverse vers User
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="achievements",
    )

    def __repr__(self) -> str:
        """Représentation textuelle du succès."""
        return f"<Achievement(id={self.id}, name={self.name!r})>"
