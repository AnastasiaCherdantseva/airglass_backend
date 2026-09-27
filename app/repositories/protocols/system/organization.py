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

    async def get_by_user_id(self, user_id: UUID) -> list[OrganizationOutPut]: ...


class OrganizationWriteRepositoryProtocol(WriteRepositoryProtocol[Organization], Protocol):
    """Write Organizations."""

    async def create_for_user(
        self, user_id: UUID, data: OrganizationData
    ) -> OrganizationOutPut: ...

    async def patch(self, data: OrganizationPatch) -> OrganizationOutPut: ...
