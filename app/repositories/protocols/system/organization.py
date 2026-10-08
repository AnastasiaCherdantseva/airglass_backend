"""
Protocols for the users repos.
"""

from typing import Protocol
from uuid import UUID

from app.dto import OrganizationData, OrganizationOutPut, OrganizationPatch
from app.models import Organization
from app.repositories.protocols import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)


class OrganizationReadRepositoryProtocol(ReadRepositoryProtocol[Organization], Protocol):
    """Read Organizations."""

    async def get_by_owner_id(self, user_id: UUID) -> list[OrganizationOutPut]: ...
    async def get_by_inn(
        self,
        inn: str,
    ) -> OrganizationOutPut | None: ...
    async def get_by_owner_id_and_name(
        self,
        user_id: UUID,
        name: str,
    ) -> OrganizationOutPut | None: ...


class OrganizationWriteRepositoryProtocol(WriteRepositoryProtocol[Organization], Protocol):
    """Write Organizations."""

    async def create_for_user(
        self, user_id: UUID, data: OrganizationData
    ) -> OrganizationOutPut: ...

    async def patch(self, data: OrganizationPatch) -> OrganizationOutPut | None: ...

    async def delete_by_owner_ids(
        self,
        owner_ids: list[UUID],
    ) -> int: ...


class OrganizationRepositoryProtocol(
    OrganizationWriteRepositoryProtocol, OrganizationReadRepositoryProtocol, Protocol
):
    pass
