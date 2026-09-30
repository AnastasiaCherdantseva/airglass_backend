"""
UserDirectPermission repository — manual overrides.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system.user_direct_permission import UserDirectPermission
from app.repositories.protocols.system.user_direct_permission import (
    UserDirectPermissionReadRepositoryProtocol,
    UserDirectPermissionWriteRepositoryProtocol,
)


class UserDirectPermissionRepository(
    UserDirectPermissionReadRepositoryProtocol,
    UserDirectPermissionWriteRepositoryProtocol,
):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_condition_ids_by_user_id(self, user_id: UUID) -> list[UUID]:
        """Все direct condition_id пользователя."""
        result = await self.db.execute(
            select(UserDirectPermission.condition_id).where(
                UserDirectPermission.user_id == user_id,
            )
        )
        return list(result.scalars().all())

    async def get_user_ids_by_condition_id(self, condition_id: UUID) -> list[UUID]:
        """Все user_id, у которых эта condition как direct."""
        result = await self.db.execute(
            select(UserDirectPermission.user_id).where(
                UserDirectPermission.condition_id == condition_id,
            )
        )
        return list(result.scalars().all())
