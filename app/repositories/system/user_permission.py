"""
UserPermission repository — materialized user permissions.
"""

from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto import (
    GroupedPermission,
    PermissionConditionAllOutPut,
)
from app.models.system.permission import Permission, PermissionZone
from app.models.system.permission_condition import PermissionCondition
from app.models.system.user_permission import UserPermission
from app.repositories.protocols.system.user_permission import (
    UserPermissionReadRepositoryProtocol,
    UserPermissionWriteRepositoryProtocol,
)


class UserPermissionRepository(
    UserPermissionReadRepositoryProtocol,
    UserPermissionWriteRepositoryProtocol,
):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_grouped_by_permission(
        self,
        user_id: UUID,
    ) -> list[GroupedPermission]:
        """Условия пользователя, сгруппированные по permission'у."""
        stmt = (
            select(
                Permission.id.label("permission_id"),
                Permission.code.label("code"),
                PermissionCondition,
            )
            .join(
                PermissionCondition,
                PermissionCondition.permission_id == Permission.id,
            )
            .join(
                UserPermission,
                UserPermission.condition_id == PermissionCondition.id,
            )
            .where(UserPermission.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        grouped: dict[UUID, GroupedPermission] = {}
        for permission_id, code, condition in rows:
            if permission_id not in grouped:
                grouped[permission_id] = GroupedPermission(
                    id=permission_id,
                    code=code,
                    conditions=[],
                )
            grouped[permission_id].conditions.append(
                PermissionConditionAllOutPut(
                    id=condition.id,
                    permission_id=condition.permission_id,
                    category_id=condition.category_id,
                    role_id=condition.role_id,
                    media_type_id=condition.media_type_id,
                    effect=condition.effect,
                    type=condition.type,
                    is_active=condition.is_active,
                )
            )
        return list(grouped.values())

    async def has_admin_access(self, user_id: UUID) -> bool:
        stmt = (
            select(Permission.id)
            .join(
                PermissionCondition,
                PermissionCondition.permission_id == Permission.id,
            )
            .join(
                UserPermission,
                UserPermission.condition_id == PermissionCondition.id,
            )
            .where(
                UserPermission.user_id == user_id,
                PermissionCondition.is_active.is_(True),
                Permission.zone == PermissionZone.ADMIN,
            )
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def replace_for_user(
        self,
        user_id: UUID,
        condition_ids: list[UUID],
    ) -> None:
        """Заменить все conditions пользователя новым набором."""
        await self.db.execute(delete(UserPermission).where(UserPermission.user_id == user_id))
        if not condition_ids:
            return
        await self.db.execute(
            insert(UserPermission),
            [{"user_id": user_id, "condition_id": cid} for cid in condition_ids],
        )

    async def delete_by_user_id(self, user_id: UUID) -> int:
        """Удалить все conditions пользователя. Возвращает rowcount."""
        result = await self.db.execute(
            delete(UserPermission).where(UserPermission.user_id == user_id)
        )
        return result.rowcount or 0
