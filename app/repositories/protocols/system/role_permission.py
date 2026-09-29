"""
Protocols for RolePermission repository.
"""

from typing import Protocol
from uuid import UUID


class RolePermissionReadRepositoryProtocol(Protocol):
    """RolePermission — read."""

    async def get_condition_ids_by_role_id(self, role_id: UUID) -> list[UUID]: ...
    async def get_role_ids_by_condition_id(self, condition_id: UUID) -> list[UUID]: ...


class RolePermissionWriteRepositoryProtocol(Protocol):
    """RolePermission — write."""

    # async def add_link(self, role_id: UUID, condition_id: UUID) -> None: ...
    # async def remove_link(self, role_id: UUID, condition_id: UUID) -> bool: ...
    # async def remove_by_role_id(self, role_id: UUID) -> int: ...
    # async def remove_by_condition_id(self, condition_id: UUID) -> int: ...


class RolePermissionRepositoryProtocol(
    RolePermissionReadRepositoryProtocol,
    RolePermissionWriteRepositoryProtocol,
    Protocol,
):
    """Full RolePermission repository."""

    pass
