"""
Protocols for the users repos.
"""

from typing import Protocol
from uuid import UUID

from app.models import User
from app.repositories.protocols import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)
from app.repositories.protocols.dto import (
    UserOutput,
    UserPatchInput,
)


class UserReadRepositoryProtocol(ReadRepositoryProtocol[User], Protocol):
    """Read users."""

    async def get_by_email(self, email: str) -> User | None: ...
    async def get_by_parent_id(self, parent_id: UUID) -> list[UserOutput]: ...


class UserWriteRepositoryProtocol(WriteRepositoryProtocol[User], Protocol):
    """Write users."""

    async def soft_delete_by_id(self, user_id: UUID) -> list[UUID]: ...
    async def patch_user(self, data: UserPatchInput) -> UserOutput | None: ...

    pass  # всё нужное — в базовом WriteRepositoryProtocol
