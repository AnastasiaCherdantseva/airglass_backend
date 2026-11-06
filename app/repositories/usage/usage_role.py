from app.models.usage.usage_role import UsageRole
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.usage.usage_role import (
    UsageRoleReadRepositoryProtocol,
    UsageRoleWriteRepositoryProtocol,
)


class UsageRoleRepository(
    BaseIdRepository[UsageRole], UsageRoleReadRepositoryProtocol, UsageRoleWriteRepositoryProtocol
):
    """Repository for usage roles.

    Репозиторий ролей использования.
    """

    model = UsageRole
