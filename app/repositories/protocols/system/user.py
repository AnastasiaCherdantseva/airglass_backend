"""
Protocols for the users repos.
"""

from typing import Protocol

from app.models import User
from app.repositories.protocols.base import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)


class UserReadRepositoryProtocol(ReadRepositoryProtocol[User], Protocol):
    """Read users."""

    async def get_by_email(self, email: str) -> User | None: ...


class UserWriteRepositoryProtocol(WriteRepositoryProtocol[User], Protocol):
    """Write users."""

    pass  # всё нужное — в базовом WriteRepositoryProtocol
