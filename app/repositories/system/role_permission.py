"""
RolePermission repository — link between role and permission condition.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.system.permission_condition import (
    PermissionConditionAllOutPut,
)
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

    async def get_conditions_by_role_id(self, role_id: UUID) -> list[PermissionConditionAllOutPut]:
        result = (
            (
                await self.db.execute(
                    select(PermissionCondition).join(
                        RolePermission, RolePermission.role_id == role_id
                    )
                )
            )
            .scalars()
            .all()
        )
        return [
            PermissionConditionAllOutPut(
                id=obj.id,
                permission_id=obj.permission_id,
                is_active=obj.is_active,
                # effect=obj.effect,
                type=obj.type,
                media_type_id=obj.media_type_id,
                category_id=obj.category_id,
                role_id=obj.role_id,
            )
            for obj in result
        ]

    async def get_conditions_by_role_ids(
        self, role_ids: list[UUID]
    ) -> dict[UUID, list[PermissionConditionAllOutPut]]:
        if not role_ids:
            return {}

        rows = (
            await self.db.execute(
                select(RolePermission.role_id, PermissionCondition)
                .join(
                    PermissionCondition,
                    RolePermission.condition_id == PermissionCondition.id,
                )
                .where(RolePermission.role_id.in_(role_ids))
            )
        ).all()

        grouped: dict[UUID, list[PermissionConditionAllOutPut]] = {}
        for role_id, condition in rows:
            grouped.setdefault(role_id, []).append(
                PermissionConditionAllOutPut(
                    id=condition.id,
                    permission_id=condition.permission_id,
                    is_active=condition.is_active,
                    type=condition.type,
                    media_type_id=condition.media_type_id,
                    category_id=condition.category_id,
                    role_id=condition.role_id,
                )
            )
        return grouped

    async def get_role_ids_by_condition_id(self, condition_id: UUID) -> list[UUID]:
        """Все role_id, к которым привязана condition."""
        result = await self.db.execute(
            select(RolePermission.role_id).where(
                RolePermission.condition_id == condition_id,
            )
        )
        return list(result.scalars().all())
