"""Service métier pour la gestion des utilisateurs.

Contient la logique de création, lecture, mise à jour
et suppression des comptes utilisateurs avec hashage
sécurisé des mots de passe.
"""
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# Contexte de hashage des mots de passe avec bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service de gestion des utilisateurs.

    Encapsule les opérations CRUD sur la table User
    et le hashage sécurisé des mots de passe.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialiser le service avec une session de base de données.

        Args:
            db: Session async SQLAlchemy.
        """
        self.db = db

    @staticmethod
    def hash_password(password: str) -> str:
        """Hasher un mot de passe en clair avec bcrypt.

        Args:
            password: Mot de passe en clair.

        Returns:
            Le hash bcrypt du mot de passe.
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifier un mot de passe contre son hash.

        Args:
            plain_password: Mot de passe en clair à vérifier.
            hashed_password: Hash bcrypt stocké en base.

        Returns:
            True si le mot de passe correspond, False sinon.
        """
        return pwd_context.verify(plain_password, hashed_password)

    async def create_user(self, user_data: UserCreate) -> User:
        """Créer un nouvel utilisateur en base de données.

        Le mot de passe est hashé avant stockage.

        Args:
            user_data: Données d'inscription validées.

        Returns:
            L'utilisateur créé avec son ID généré.
        """
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=self.hash_password(user_data.password),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user(self, user_id: UUID) -> User | None:
        """Récupérer un utilisateur par son identifiant UUID.

        Args:
            user_id: UUID de l'utilisateur.

        Returns:
            L'utilisateur trouvé ou None.
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Récupérer un utilisateur par son adresse email.

        Args:
            email: Adresse email à rechercher.

        Returns:
            L'utilisateur trouvé ou None.
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Récupérer un utilisateur par son nom d'utilisateur.

        Args:
            username: Nom d'utilisateur à rechercher.

        Returns:
            L'utilisateur trouvé ou None.
        """
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user_id: UUID, update_data: UserUpdate) -> User:
        """Mettre à jour les informations d'un utilisateur.

        Seuls les champs non-None sont mis à jour (update partiel).

        Args:
            user_id: UUID de l'utilisateur à modifier.
            update_data: Champs à mettre à jour.

        Returns:
            L'utilisateur mis à jour.

        Raises:
            ValueError: Si l'utilisateur n'existe pas.
        """
        user = await self.get_user(user_id)
        if not user:
            raise ValueError(f"Utilisateur {user_id} non trouvé")

        update_fields = update_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: UUID) -> None:
        """Supprimer un utilisateur de la base de données.

        La suppression en cascade supprime également les
        temps de résolution et succès associés.

        Args:
            user_id: UUID de l'utilisateur à supprimer.

        Raises:
            ValueError: Si l'utilisateur n'existe pas.
        """
        user = await self.get_user(user_id)
        if not user:
            raise ValueError(f"Utilisateur {user_id} non trouvé")

        await self.db.delete(user)
        await self.db.commit()
