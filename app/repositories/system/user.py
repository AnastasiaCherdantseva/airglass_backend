"""
Репозиторий пользователей.
"""

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, text

from app.dto import UserCreateFull, UserOutput, UserPatchInput
from app.models import User
from app.repositories.base import BaseIdRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseIdRepository[User]):
    """
    SQLAlchemy-реализация репозитория аутентификации пользователей.

    Наследует get_by_id, add, delete, flush от BaseIdRepository.
    Добавляет get_by_email
    """

    model = User

    async def get_subtree(self, user_id: UUID) -> list[User]:
        anchor = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        subtree = anchor.cte(name="subtree", recursive=True)

        subtree_alias = subtree.alias()
        recursive = (
            select(User)
            .join(subtree_alias, User.parent_id == subtree_alias.c.id)
            .where(User.deleted_at.is_(None))
        )
        subtree = subtree.union_all(recursive)

        stmt = select(User).where(User.id.in_(select(subtree.c.id)))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def is_in_subtree(self, root_id: UUID, user_id: UUID) -> bool:
        stmt = text(
            """
            WITH RECURSIVE subtree AS (
                SELECT id
                FROM users
                WHERE id = :root_id
                AND deleted_at IS NULL
                UNION ALL
                SELECT u.id
                FROM users u
                JOIN subtree s ON u.parent_id = s.id
                WHERE u.deleted_at IS NULL
            )
            SELECT EXISTS (
                SELECT 1 FROM subtree WHERE id = :user_id
            )
            """
        )
        result = await self.db.scalar(
            stmt,
            {"root_id": root_id, "user_id": user_id},
        )
        return bool(result)

    async def _count_children_by_parent_ids(
        self,
        parent_ids: list[UUID],
    ) -> dict[UUID, int]:
        """Количество прямых живых детей для каждого parent_id."""
        if not parent_ids:
            return {}
        stmt = (
            select(User.parent_id, func.count(User.id))
            .where(
                User.parent_id.in_(parent_ids),
                User.deleted_at.is_(None),
            )
            .group_by(User.parent_id)
        )
        result = await self.db.execute(stmt)
        counts = {parent_id: count for parent_id, count in result.all()}
        return {pid: counts.get(pid, 0) for pid in parent_ids}

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
        self, parent_id: UUID, *, limit: int = 10, page: int = 0
    ) -> list[UserOutput]:
        # Удаленные пользователи не попадают
        offset = (page - 1) * limit
        stmt = (
            select(User)
            .where(
                User.parent_id == parent_id,
                User.deleted_at.is_(None),
            )
            .order_by(User.created_at, User.id)
            .limit(limit)
            .offset(offset=offset)
        )
        result = await self.db.scalars(stmt)
        users = result.all()
        if not users:
            return []
        children_counts = await self._count_children_by_parent_ids([u.id for u in users])
        # 9. Сборка DTO
        return [
            UserOutput(
                id=row.id,
                parent_id=row.parent_id,
                email=row.email,
                name=row.name,
                is_active=row.is_active,
                children_count=children_counts[row.id],
                email_verified=row.email_verified is not None,
            )
            for row in users
        ]

    async def count_by_parent_id(
        self,
        parent_id: UUID,
    ) -> int:
        stmt = select(func.count(User.id)).where(
            User.parent_id == parent_id,
            User.deleted_at.is_(None),
        )
        result = await self.db.scalar(stmt)
        return result or 0

    async def soft_delete_by_id(self, user_id: UUID) -> int:
        deleted_time = datetime.now(UTC)
        users = await self.get_subtree(user_id)
        if not users:
            return 0

        for user in users:
            user.is_active = False
            user.deleted_at = deleted_time
        await self.flush()
        return len(users)

    async def patch_user(self, data: UserPatchInput) -> UserOutput | None:
        user = await self.get_by_id(data.id)

        if user is None:
            return None

        if data.email is not None:
            normalized = data.email.strip().lower()
            user.email = normalized

        if data.name is not None:
            user.name = data.name

        if data.new_password_hash is not None:
            user.password_hash = data.new_password_hash

        await self.flush()
        await self.db.refresh(user, ["children"])
        return UserOutput(
            id=user.id,
            parent_id=user.parent_id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            children_count=sum(1 for c in user.children if c.deleted_at is None),
            email_verified=user.email_verified is not None,
        )

    async def create(self, data: UserCreateFull) -> UserOutput:
        normalized = data.email.strip().lower()
        user = User(
            parent_id=data.parent_id,
            # is_active=data.is_active,
            email=normalized,
            name=data.name,
            password_hash=data.password_hash,
            email_verified=datetime.now(UTC),
            is_active=True,
        )
        self.add(user)
        await self.flush()

        return UserOutput(
            id=user.id,
            parent_id=user.parent_id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            children_count=0,
            email_verified=user.email_verified is not None,
        )
