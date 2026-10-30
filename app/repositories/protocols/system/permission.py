"""
Protocols for the users repos.
"""

from typing import Protocol
from uuid import UUID

from app.dto import PermissionOutput
from app.models import Permission
from app.repositories.protocols import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)


class PermissionReadRepositoryProtocol(ReadRepositoryProtocol[Permission], Protocol):
    """Read Permissions."""

    async def get_by_code(self, code: str) -> PermissionOutput | None: ...
    async def get_by_conditions(self, condition_ids:list[UUID]) -> dict[PermissionOutput, list[UUID]]: ...


class PermissionWriteRepositoryProtocol(WriteRepositoryProtocol[Permission], Protocol):
    """Write Permissions."""

    pass
