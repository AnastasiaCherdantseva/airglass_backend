"""
Fake-реализация UserRepository для юнит-тестов.

In-memory: хранит пользователей в словаре, не ходит в БД.
Структурно подходит под UserReadRepositoryProtocol и
UserWriteRepositoryProtocol — наследование не нужно.
"""
# from uuid import uuid4

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
        """Найти по id."""
        return self.users.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        """Найти по email. Регистронезависимое сравнение (ADR-USER-002)."""
        normalized = email.strip().lower()
        return next(
            (u for u in self.users.values() if u.email.lower() == normalized),
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
            )
            for u in page_items
        ]

    async def count_by_parent_id(self, parent_id: UUID) -> int:
        """Количество прямых детей (без мягко удалённых)."""
        return sum(
            1 for u in self.users.values() if u.parent_id == parent_id and u.deleted_at is None
        )

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
        )
        self.add(user)
        return UserOutput(
            id=user.id,
            parent_id=user.parent_id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            children_count=0,
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
