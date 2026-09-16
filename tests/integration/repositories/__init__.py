"""
Fake-реализация UserRepository для юнит-тестов.

In-memory: хранит пользователей в словаре, не ходит в БД.
Структурно подходит под UserReadRepositoryProtocol и
UserWriteRepositoryProtocol — наследование не нужно.
"""

from uuid import UUID

from app.models import User


class FakeUserRepository:
    """In-memory реализация UserRepository."""

    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Найти по id."""
        return self.users.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        """Найти по email."""
        return next(
            (u for u in self.users.values() if u.email == email),
            None,
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