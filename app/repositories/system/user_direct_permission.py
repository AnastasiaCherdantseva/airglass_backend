"""
UserDirectPermission repository — manual overrides.
"""

from uuid import UUID

from sqlalchemy import delete, insert, select
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

    async def remove_by_user_ids(self, user_ids: list[UUID]) -> int:
        stmt = delete(UserDirectPermission).where(UserDirectPermission.user_id.in_(user_ids))
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount

    async def add_link(self, user_id: UUID, condition_id: UUID) -> None:
        await self.db.execute(
            insert(UserDirectPermission).values(user_id=user_id, condition_id=condition_id)
        )
        await self.db.flush()

    async def add_links(self, user_id: UUID, condition_ids: list[UUID]) -> int:
        if not condition_ids:
            return 0
        result = await self.db.execute(
            insert(UserDirectPermission).values(
                [
                    {"user_id": user_id, "condition_id": condition_id}
                    for condition_id in condition_ids
                ]
            )
        )
        return result.rowcount
