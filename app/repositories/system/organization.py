from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto import OrganizationData, OrganizationOutPut, OrganizationPatch
from app.models import Organization
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.system.organization import (
    OrganizationReadRepositoryProtocol,
    OrganizationWriteRepositoryProtocol,
)


class OrganizationRepository(
    BaseIdRepository[Organization],
    OrganizationReadRepositoryProtocol,
    OrganizationWriteRepositoryProtocol,
):
    """Репозиторий для работы с организациями."""

    model = Organization

    def __init__(self, db: AsyncSession) -> None:
        """Инициализировать репозиторий."""
        self.db = db

    def _to_output(self, organization: Organization) -> OrganizationOutPut:
        """Преобразовать модель организации в DTO."""
        return OrganizationOutPut(
            id=organization.id,
            owner_id=organization.owner_id,
            name=organization.name,
            inn=organization.inn,
            address=organization.address,
            created_at=organization.created_at,
            updated_at=organization.updated_at,
        )

    async def get_by_owner_id(
        self,
        user_id: UUID,
    ) -> list[OrganizationOutPut]:
        """Получить организации, в которых пользователь является участником."""
        stmt = select(Organization).where(Organization.owner_id == user_id)

        result = await self.db.execute(stmt)
        return [self._to_output(row) for row in result.scalars().all()]

    async def create_for_user(
        self,
        user_id: UUID,
        data: OrganizationData,
    ) -> OrganizationOutPut:
        """Создать организацию с указанным пользователем в качестве владельца."""
        organization = Organization(
            owner_id=user_id,
            name=data.name,
            inn=data.inn,
            address=data.address,
        )
        self.add(organization)
        await self.flush()

        return self._to_output(organization)

    async def patch(
        self,
        data: OrganizationPatch,
    ) -> OrganizationOutPut | None:
        """Обновить организацию."""
        organization = await self.get_by_id(data.id)
        if organization is None:
            return None
        if data.name is not None:
            organization.name = data.name
        if data.inn is not None:
            organization.inn = data.inn
        if data.address is not None:
            organization.address = data.address
        await self.flush()

        return self._to_output(organization)

    async def delete_by_owner_ids(
        self,
        owner_ids: list[UUID],
    ) -> int:
        """Удалить организации указанных владельцев."""
        if not owner_ids:
            return 0

        result = await self.db.execute(
            delete(Organization).where(Organization.owner_id.in_(owner_ids))
        )
        return result.rowcount or 0
