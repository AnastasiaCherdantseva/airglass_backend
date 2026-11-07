from typing import Protocol

from app.dto.usage.usage_role import UsageRoleOutput
from app.models.usage.usage_role import UsageRole
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class UsageRoleReadRepositoryProtocol(
    ReadRepositoryProtocol[UsageRole],
    Protocol,
):
    async def get_all(self) -> list[UsageRoleOutput]: ...


class UsageRoleWriteRepositoryProtocol(
    WriteRepositoryProtocol[UsageRole],
    Protocol,
):
    pass


class UsageRoleRepositoryProtocol(
    UsageRoleReadRepositoryProtocol,
    UsageRoleWriteRepositoryProtocol,
    Protocol,
):
    pass
