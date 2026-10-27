"""
Fake-реализация UserRepository для юнит-тестов.

In-memory: хранит пользователей в словаре, не ходит в БД.
Структурно подходит под UserReadRepositoryProtocol и
UserWriteRepositoryProtocol — наследование не нужно.
"""
# from uuid import uuid4

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.dto import UserCreateFull, UserOutput
from app.models import User


class FakeUserRepository:
    """In-memory реализация UserRepository."""

    def __init__(self, initial_users: list[User] | None = None) -> None:
        self.users: dict[UUID, User] = {}
        if initial_users:
            for u in initial_users:
                self.add(u)

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Найти по id. Мягко удалённые не возвращаются (как в реальном репозитории)."""
        user = self.users.get(user_id)
        if user is None or user.deleted_at is not None:
            return None
        return user

    async def get_subtree(self, user_id: UUID) -> list[User]:
        """Return an active user and all active descendants (mirrors UserRepository).

        Возвращает активного пользователя и всех активных потомков.
        """
        root = self.users.get(user_id)
        if root is None or root.deleted_at is not None:
            return []
        result: list[User] = [root]
        stack = [root.id]
        while stack:
            current_id = stack.pop()
            for u in self.users.values():
                if u.parent_id == current_id and u.deleted_at is None:
                    result.append(u)
                    stack.append(u.id)
        return result

    async def is_in_subtree(self, root_id: UUID, user_id: UUID) -> bool:
        """True if user is root or its active descendant (mirrors UserRepository).

        True, если пользователь — корень или его активный потомок.
        """
        root = self.users.get(root_id)
        if root is None or root.deleted_at is not None:
            return False
        if root_id == user_id:
            return True
        subtree = await self.get_subtree(root_id)
        return any(u.id == user_id for u in subtree)

    async def get_by_email(self, email: str) -> User | None:
        """Найти по email. Регистронезависимое сравнение (ADR-USER-002)."""
        normalized = email.strip().lower()
        return next(
            (
                u
                for u in self.users.values()
                if u.email.lower() == normalized and u.deleted_at is None
            ),
            None,
        )

    async def get_by_parent_id(
        self,
        parent_id: UUID,
        *,
        limit: int = 10,
        page: int = 0,
    ) -> list[UserOutput]:
        """
        Прямые дети parent_id с пагинацией.

        Сортировка: created_at ASC, id ASC (как в реальном репозитории).
        """
        children = [
            u for u in self.users.values() if u.parent_id == parent_id and u.deleted_at is None
        ]
        children.sort(key=lambda u: (u.created_at, u.id))
        offset = page * limit
        page_items = children[offset : offset + limit]

        return [
            UserOutput(
                id=u.id,
                parent_id=u.parent_id,
                email=u.email,
                name=u.name,
                is_active=u.is_active,
                children_count=sum(
                    1 for x in self.users.values() if x.parent_id == u.id and x.deleted_at is None
                ),
                email_verified=u.email_verified is not None,
            )
            for u in page_items
        ]

    async def count_by_parent_id(self, parent_id: UUID) -> int:
        """Количество прямых детей (без мягко удалённых)."""
        return sum(
            1 for u in self.users.values() if u.parent_id == parent_id and u.deleted_at is None
        )

    # ========================================
    # ЗАПИСЬ
    # ========================================

    def add(self, user: User) -> None:
        """Добавить пользователя в память."""
        self.users[user.id] = user

    async def delete(self, user: User) -> None:
        """Удалить пользователя из памяти."""
        self.users.pop(user.id, None)

    async def flush(self) -> None:
        """No-op: в памяти всё уже на месте."""
        pass

    async def create(self, data: UserCreateFull) -> UserOutput:
        """
        Create a user in memory (mirrors UserRepository.create).

        Создать пользователя в памяти (повторяет UserRepository.create).
        """
        user = User(
            id=uuid4(),
            parent_id=data.parent_id,
            is_active=data.is_active,
            email=data.email.strip().lower(),
            name=data.name,
            password_hash=data.password_hash,
            email_verified=None,
        )
        self.add(user)
        return UserOutput(
            id=user.id,
            parent_id=user.parent_id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            children_count=0,
            email_verified=user.email_verified is not None,
        )

    async def soft_delete_by_id(self, user_id: UUID) -> int:
        """Soft-delete user and active descendants with shared timestamp.

        Мягко удаляет пользователя и активных потомков с общим timestamp.
        """
        users = await self.get_subtree(user_id)
        if not users:
            return 0
        deleted_at = datetime.now(UTC)
        for u in users:
            u.is_active = False
            u.deleted_at = deleted_at
        return len(users)
