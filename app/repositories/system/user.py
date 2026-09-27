"""
Репозиторий пользователей.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select

from app.models import User
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.dto.system.user import UserOutput, UserPatchInput


class UserRepository(BaseIdRepository[User]):
    """
    SQLAlchemy-реализация репозитория аутентификации пользователей.

    Наследует get_by_id, add, delete, flush от BaseIdRepository.
    Добавляет get_by_email
    """

    model = User

    async def _get_subtree(self, user_id: UUID) -> list[User]:
        anchor = select(User).where(User.id == user_id)
        subtree = anchor.cte(name="subtree", recursive=True)

        subtree_alias = subtree.alias()
        user_alias = User.__table__.alias()

        recursive = select(user_alias).where(user_alias.c.parent_id == subtree_alias.c.id)

        subtree = subtree.union_all(recursive)

        result = await self.db.execute(select(subtree))
        return list(result.scalars().all())

    async def get_by_email(self, email: str) -> User | None:
        """Найти пользователя по email."""
        # ADR-USER-002
        normalized = email.strip().lower()

        result = await self.db.execute(
            select(User).where(
                func.lower(User.email) == normalized,
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_parent_id(
        self,
        parent_id: UUID,
    ) -> list[UserOutput]:
        # тип выходных данных гарантирует отдачу без мягких полей (по типу password_hash)
        users = await self._get_subtree(parent_id)
        if not users:
            return []

        # 9. Сборка DTO
        return [
            UserOutput(
                id=row.id,
                parent_id=row.parent_id,
                email=row.email,
                name=row.name,
                is_active=row.is_active,
            )
            for row in users
        ]

    async def soft_delete_by_id(self, user_id: UUID) -> list[UUID]:
        deleted_time = datetime.now(UTC)

        users = await self._get_subtree(user_id)
        if not users:
            return []

        user_ids = []
        for user in users:
            user.is_active = False
            user.deleted_at = deleted_time
            user_ids.append(user.id)
        await self.flush()
        return user_ids

    async def patch_user(self, data: UserPatchInput) -> UserOutput | None:
        user = await self.get_by_id(data.id)
        if user is None:
            return None

        if data.email is not None:
            user.email = data.email

        if data.name is not None:
            user.name = data.name

        if data.new_password_hash is not None:
            user.password_hash = data.new_password_hash

        await self.flush()

        return UserOutput(
            id=user.id,
            parent_id=user.parent_id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
        )
