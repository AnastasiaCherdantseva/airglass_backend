"""
Protocols for the users repos.
"""

from typing import Protocol
from uuid import UUID

from app.models import Role
from app.repositories.protocols import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)
from app.repositories.protocols.dto import RoleData, RoleOutput, RolePatchData


class RoleReadRepositoryProtocol(ReadRepositoryProtocol[Role], Protocol):
    """Read Organizations."""

    async def get_by_owner_id(self, owner_id: UUID) -> list[RoleOutput]: ...


class RoleWriteRepositoryProtocol(WriteRepositoryProtocol[Role], Protocol):
    """Write Organizations."""

    async def activate_by_ids(self, role_ids: list[UUID]) -> int: ...
    async def deactivate_by_ids(self, role_ids: list[UUID]) -> int: ...

    async def activate_by_owner_ids(self, owner_ids: list[UUID]) -> int: ...
    async def deactivate_by_owner_ids(self, owner_ids: list[UUID]) -> int: ...

    async def create_by_user(self, user_id: UUID, data: RoleData) -> RoleOutput | None: ...
    async def delete_by_owner_ids(self, owner_ids: list[UUID]) -> int: ...

    async def patch(self, data: RolePatchData) -> RoleOutput | None: ...
