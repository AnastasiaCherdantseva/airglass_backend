"""
Protocols for the users repos.
"""

from typing import Protocol
from uuid import UUID

from app.dto import UserCreateFull, UserOutput, UserPatchInput
from app.models import User
from app.repositories.protocols import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)


class UserReadRepositoryProtocol(ReadRepositoryProtocol[User], Protocol):
    """Read users."""

    async def get_by_email(self, email: str) -> User | None: ...
    async def get_by_parent_id(
        self, parent_id: UUID, *, limit: int = 10, page: int = 0
    ) -> list[UserOutput]: ...
    async def count_by_parent_id(
        self,
        parent_id: UUID,
    ) -> int: ...


class UserWriteRepositoryProtocol(WriteRepositoryProtocol[User], Protocol):
    """Write users."""

    async def soft_delete_by_id(self, user_id: UUID) -> list[UUID]: ...
    async def patch_user(self, data: UserPatchInput) -> UserOutput | None: ...
    async def create(self, data: UserCreateFull) -> UserOutput: ...


class UserRepositoryProtocol(UserWriteRepositoryProtocol, UserReadRepositoryProtocol, Protocol):
    pass
