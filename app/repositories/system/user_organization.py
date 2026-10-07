from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.system.organization import OrganizationOutPut
from app.models import UserOrganization
from app.models.system.organizations import Organization
from app.repositories.protocols.system.user_organization import (
    UserOrganizationReadRepositoryProtocol,
    UserOrganizationWriteRepositoryProtocol,
)


class UserOrganizationRepository(
    UserOrganizationReadRepositoryProtocol,
    UserOrganizationWriteRepositoryProtocol,
):
    """Репозиторий связей пользователей и организаций."""

    def __init__(self, db: AsyncSession) -> None:
        """Инициализировать репозиторий."""
        self.db = db

    async def get_user_ids_by_organization_id(
        self,
        organization_id: UUID,
    ) -> list[UUID]:
        """Получить ID пользователей организации."""
        result = await self.db.execute(
            select(UserOrganization.user_id).where(
                UserOrganization.organization_id == organization_id,
            )
        )
        return list(result.scalars().all())

    async def get_organization_ids_by_user_id(
        self,
        user_id: UUID,
    ) -> list[UUID]:
        """Получить ID организаций пользователя."""
        result = await self.db.execute(
            select(UserOrganization.organization_id).where(
                UserOrganization.user_id == user_id,
            )
        )
        return list(result.scalars().all())

    async def get_organizations_by_user_id(
        self,
        user_id: UUID,
    ) -> list[OrganizationOutPut]:
        """Получить организаций с которыми юзер имеет связь."""
        req = await self.db.execute(
            select(Organization)
            .join(UserOrganization, UserOrganization.organization_id == Organization.id)
            .where(
                UserOrganization.user_id == user_id,
            )
        )
        result = req.scalars().all()
        return [
            OrganizationOutPut(
                id=organization.id,
                owner_id=organization.owner_id,
                name=organization.name,
                inn=organization.inn,
                address=organization.address,
                created_at=organization.created_at,
                updated_at=organization.updated_at,
            )
            for organization in result
        ]

    async def add_link(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> None:
        """Создать связь пользователя с организацией."""
        self.db.add(
            UserOrganization(
                user_id=user_id,
                organization_id=organization_id,
            )
        )
        await self.db.flush()

    async def remove_link(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> bool:
        """Удалить связь пользователя с организацией."""
        result = await self.db.execute(
            delete(UserOrganization).where(
                UserOrganization.user_id == user_id,
                UserOrganization.organization_id == organization_id,
            )
        )
        await self.db.flush()

        return result.rowcount > 0

    async def remove_by_user_id(
        self,
        user_id: UUID,
    ) -> int:
        """Удалить все связи пользователя с организациями."""
        result = await self.db.execute(
            delete(UserOrganization).where(
                UserOrganization.user_id == user_id,
            )
        )
        await self.db.flush()

        return result.rowcount or 0

    async def remove_by_organization_id(
        self,
        organization_id: UUID,
    ) -> int:
        """Удалить все связи организации с пользователями."""
        result = await self.db.execute(
            delete(UserOrganization).where(
                UserOrganization.organization_id == organization_id,
            )
        )
        await self.db.flush()

        return result.rowcount or 0
