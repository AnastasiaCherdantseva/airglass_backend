"""
RolePermission repository — link between role and permission condition.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system.role_permission import RolePermission
from app.repositories.protocols.system.role_permission import (
    RolePermissionReadRepositoryProtocol,
    RolePermissionWriteRepositoryProtocol,
)


class RolePermissionRepository(
    RolePermissionReadRepositoryProtocol,
    RolePermissionWriteRepositoryProtocol,
):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_condition_ids_by_role_id(self, role_id: UUID) -> list[UUID]:
        """Все condition_id, привязанные к роли."""
        result = await self.db.execute(
            select(RolePermission.condition_id).where(
                RolePermission.role_id == role_id,
            )
        )
        return list(result.scalars().all())

    async def get_role_ids_by_condition_id(self, condition_id: UUID) -> list[UUID]:
        """Все role_id, к которым привязана condition."""
        result = await self.db.execute(
            select(RolePermission.role_id).where(
                RolePermission.condition_id == condition_id,
            )
        )
        return list(result.scalars().all())
