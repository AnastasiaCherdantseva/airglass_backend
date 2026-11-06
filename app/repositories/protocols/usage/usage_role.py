from typing import Protocol

from app.models.usage.usage_role import UsageRole
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class UsageRoleRepositoryProtocol(
    ReadRepositoryProtocol[UsageRole],
    WriteRepositoryProtocol[UsageRole],
    Protocol,
):
    """Repository contract for usage roles.

    Контракт репозитория ролей использования товаров.
    """
