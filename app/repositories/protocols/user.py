"""
Protocol-контракты для репозитория пользователей.
"""

from typing import Protocol

from app.models import User
from app.repositories.protocols.base import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)


class UserReadRepositoryProtocol(ReadRepositoryProtocol[User], Protocol):
    """Чтение пользователей."""

    async def get_by_email(self, email: str) -> User | None: ...


class UserWriteRepositoryProtocol(WriteRepositoryProtocol[User], Protocol):
    """Запись пользователей."""

    pass   # всё нужное — в базовом WriteRepositoryProtocol