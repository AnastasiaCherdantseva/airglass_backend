from sqlalchemy import select

from app.dto.usage.usage_role import UsageRoleOutput
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

    async def get_all(self) -> list[UsageRoleOutput]:
        execute = await self.db.execute(select(UsageRole))
        result = execute.scalars().all()
        return [
            UsageRoleOutput(id=ur.id, name=ur.name, description=ur.description) for ur in result
        ]
