"""
Protocols for UserDirectPermission repository.
"""

from typing import Protocol
from uuid import UUID


class UserDirectPermissionReadRepositoryProtocol(Protocol):
    """UserDirectPermission — read."""

    async def get_condition_ids_by_user_id(self, user_id: UUID) -> list[UUID]: ...
    async def get_user_ids_by_condition_id(self, condition_id: UUID) -> list[UUID]: ...


class UserDirectPermissionWriteRepositoryProtocol(Protocol):
    """UserDirectPermission — write."""

    # async def add_link(self, user_id: UUID, condition_id: UUID) -> None: ...
    # async def remove_link(self, user_id: UUID, condition_id: UUID) -> bool: ...
    # async def remove_by_user_id(self, user_id: UUID) -> int: ...
    # async def remove_by_condition_id(self, condition_id: UUID) -> int: ...


class UserDirectPermissionRepositoryProtocol(
    UserDirectPermissionReadRepositoryProtocol,
    UserDirectPermissionWriteRepositoryProtocol,
    Protocol,
):
    """Full UserDirectPermission repository."""

    pass
