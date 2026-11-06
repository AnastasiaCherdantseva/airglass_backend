from typing import Protocol

from app.models.usage.usage_role import UsageRole
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class UsageRoleReadRepositoryProtocol(
    ReadRepositoryProtocol[UsageRole],
    Protocol,
):
    pass


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
