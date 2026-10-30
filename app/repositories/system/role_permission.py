"""
RolePermission repository — link between role and permission condition.
"""

from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.system.permission_condition import (
    PermissionConditionAllOutPut,
)
from app.dto.system.user_permission import GroupedPermission
from app.models.system.permission import Permission
from app.models.system.permission_condition import PermissionCondition
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

    async def get_conditions_by_role_ids(
        self,
        role_ids: list[UUID],
    ) -> dict[UUID, list[GroupedPermission]]:
        if not role_ids:
            return {}

        stmt = (
            select(
                RolePermission.role_id.label("role_id"),
                Permission.id.label("permission_id"),
                Permission.code.label("code"),
                PermissionCondition,
            )
            .join(
                PermissionCondition,
                PermissionCondition.id == RolePermission.condition_id,
            )
            .join(
                Permission,
                Permission.id == PermissionCondition.permission_id,
            )
            .where(RolePermission.role_id.in_(role_ids))
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        grouped: dict[UUID, dict[UUID, GroupedPermission]] = {}
        for role_id, permission_id, code, condition in rows:
            role_group = grouped.setdefault(role_id, {})
            if permission_id not in role_group:
                role_group[permission_id] = GroupedPermission(
                    id=permission_id,
                    code=code,
                    conditions=[],
                )
            role_group[permission_id].conditions.append(
                PermissionConditionAllOutPut(
                    id=condition.id,
                    permission_id=condition.permission_id,
                    category_id=condition.category_id,
                    role_id=condition.role_id,
                    media_type_id=condition.media_type_id,
                    type=condition.type,
                    is_active=condition.is_active,
                )
            )
        return {rid: list(g.values()) for rid, g in grouped.items()}

    async def get_role_ids_by_condition_id(self, condition_id: UUID) -> list[UUID]:
        """Все role_id, к которым привязана condition."""
        result = await self.db.execute(
            select(RolePermission.role_id).where(
                RolePermission.condition_id == condition_id,
            )
        )
        return list(result.scalars().all())

    # WRITE

    async def add_links_for_role(self, role_id:UUID, condition_ids:list[UUID]) -> int: 
        if not condition_ids:
            return 0
        stmt = (
            insert(RolePermission)
            .values([
                {"role_id": role_id, "condition_id": condition_id}
                for condition_id in condition_ids
            ])
            .returning(RolePermission.condition_id) 
        )
        result = await self.db.execute(stmt)
        return result.rowcount