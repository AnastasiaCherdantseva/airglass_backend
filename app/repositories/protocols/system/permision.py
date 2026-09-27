"""
Protocols for the users repos.
"""

from typing import Protocol
from uuid import UUID

from app.models import Permission
from app.repositories.protocols import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)
from app.repositories.protocols.dto import PermissionData


class PermissionReadRepositoryProtocol(ReadRepositoryProtocol[Permission], Protocol):
    """Read Permissions."""

    async def get_by_code(self, code: str) -> PermissionData | None: ...


class PermissionWriteRepositoryProtocol(WriteRepositoryProtocol[Permission], Protocol):
    """Write Permissions."""

    async def deactivate_by_ids(self, permission_ids: list[UUID]) -> int: ...
    async def activate_by_ids(self, permission_ids: list[UUID]) -> int: ...
