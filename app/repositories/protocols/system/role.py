"""
Protocols for the users repos.
"""

from typing import Protocol
from uuid import UUID

from app.dto import RoleData, RoleOutput, RolePatchData
from app.dto.system.role import RoleCreate
from app.models import Role
from app.repositories.protocols import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)


class RoleReadRepositoryProtocol(ReadRepositoryProtocol[Role], Protocol):
    """Read Organizations."""

    async def get_by_owner_id(
        self,
        owner_id: UUID,
        *,
        is_active: bool | None = None,
    ) -> list[RoleOutput]: ...
    async def get_by_owner_id_and_name(
        self,
        owner_id: UUID,
        name: str,
    ) -> RoleOutput | None: ...

    async def get_by_ids(self, ids: list[UUID]) -> list[RoleOutput]: ...
    async def get_ids_by_owner_ids(
        self,
        owner_ids: list[UUID],
        *,
        is_active: bool | None = None,
    ) -> list[RoleOutput]: ...


class RoleWriteRepositoryProtocol(WriteRepositoryProtocol[Role], Protocol):
    """Write Organizations."""

    async def activate_by_ids(self, role_ids: list[UUID]) -> int: ...
    async def deactivate_by_ids(self, role_ids: list[UUID]) -> int: ...

    # async def activate_by_owner_ids(self, owner_ids: list[UUID]) -> int: ...
    # async def deactivate_by_owner_ids(self, owner_ids: list[UUID]) -> int: ...

    async def create(self, data: RoleCreate) -> RoleOutput: ...

    async def delete_by_owner_ids(self, owner_ids: list[UUID]) -> int: ...

    async def patch(self, data: RolePatchData) -> RoleOutput | None: ...


class RoleRepositoryProtocol(RoleWriteRepositoryProtocol, RoleReadRepositoryProtocol, Protocol):
    pass
