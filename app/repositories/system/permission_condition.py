"""
Session repo.
"""

from uuid import UUID

from sqlalchemy import Select, select, update

from app.dto import (
    PermissionConditionAllOutPut,
    PermissionConditionCategoryOutPut,
    PermissionConditionMediaOutPut,
    PermissionConditionRoleOutPut,
)
from app.models import ConditionType, PermissionCondition, PermissionEffect
from app.repositories.base import BaseIdRepository


class PermissionConditionRepository(BaseIdRepository[PermissionCondition]):
    model = PermissionCondition

    def _filter(
        self,
        stmt: Select[tuple[PermissionCondition]],
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
        condition_type: ConditionType | None = None,
    ) -> Select[tuple[PermissionCondition]]:
        if is_active is not None:
            stmt = stmt.where(PermissionCondition.is_active.is_(is_active))
        if effect is not None:
            stmt = stmt.where(PermissionCondition.effect == effect)
        if condition_type is not None:
            stmt = stmt.where(PermissionCondition.type == condition_type)
        return stmt

    def _to_all_output(self, p: PermissionCondition) -> PermissionConditionAllOutPut:
        return PermissionConditionAllOutPut(
            id=p.id,
            permission_id=p.permission_id,
            category_id=p.category_id,
            role_id=p.role_id,
            media_type_id=p.media_type_id,
            effect=p.effect,
            type=p.type,
            is_active=p.is_active,
        )

    async def get_by_role(
        self,
        role_id: UUID,
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
    ) -> list[PermissionConditionRoleOutPut]:
        """Получить conditions типа ROLE для указанной роли."""
        stmt = select(PermissionCondition).where(
            PermissionCondition.type == ConditionType.ROLE,
            PermissionCondition.role_id == role_id,
        )
        stmt = self._filter(stmt, is_active=is_active, effect=effect)
        result = await self.db.execute(stmt)
        permissions = result.scalars().all()
        returned: list[PermissionConditionRoleOutPut] = []
        for p in permissions:
            # Гарантировано CHECK-констрейнтом ck_permission_condition_type
            # для type='ROLE': role_id IS NOT NULL.
            assert p.role_id is not None
            returned.append(
                PermissionConditionRoleOutPut(
                    id=p.id,
                    permission_id=p.permission_id,
                    role_id=p.role_id,
                    effect=p.effect,
                    type=p.type,
                    is_active=p.is_active,
                )
            )
        return returned

    async def get_by_category(
        self,
        category_id: UUID,
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
    ) -> list[PermissionConditionCategoryOutPut]:
        """Получить conditions типа CATEGORY для указанной КАТЕГОРИИ."""
        stmt = select(PermissionCondition).where(
            PermissionCondition.type == ConditionType.CATEGORY,
            (PermissionCondition.category_id == category_id),
        )
        stmt = self._filter(stmt, is_active=is_active, effect=effect)
        result = await self.db.execute(stmt)
        permissions = result.scalars().all()
        returned: list[PermissionConditionCategoryOutPut] = []
        for p in permissions:
            assert p.category_id is not None
            returned.append(
                PermissionConditionCategoryOutPut(
                    id=p.id,
                    permission_id=p.permission_id,
                    category_id=p.category_id,
                    effect=p.effect,
                    type=p.type,
                    is_active=p.is_active,
                )
            )
        return returned

    async def get_by_media_type(
        self,
        media_type_id: UUID,
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
    ) -> list[PermissionConditionMediaOutPut]:
        """Получить conditions типа MEDIA_TYPE для указанноГО ТИПА МЕДИА."""
        stmt = select(PermissionCondition).where(
            (PermissionCondition.type == ConditionType.MEDIA),
            (PermissionCondition.media_type_id == media_type_id),
        )
        stmt = self._filter(stmt, is_active=is_active, effect=effect)
        result = await self.db.execute(stmt)

        permissions = result.scalars().all()
        returned: list[PermissionConditionMediaOutPut] = []
        for p in permissions:
            assert p.media_type_id is not None
            returned.append(
                PermissionConditionMediaOutPut(
                    id=p.id,
                    permission_id=p.permission_id,
                    media_type_id=p.media_type_id,
                    effect=p.effect,
                    type=p.type,
                    is_active=p.is_active,
                )
            )
        return returned

    async def get_by_permission(
        self,
        permission_id: UUID,
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
        condition_type: ConditionType | None = None,
    ) -> list[PermissionConditionAllOutPut]:

        stmt = select(PermissionCondition).where(
            (PermissionCondition.permission_id == permission_id),
        )
        stmt = self._filter(stmt, is_active=is_active, effect=effect, condition_type=condition_type)
        result = await self.db.execute(stmt)

        permissions = result.scalars().all()
        return [self._to_all_output(p) for p in permissions]

    async def get_by_ids(self, ids: list[UUID]) -> list[PermissionConditionAllOutPut]:
        if not ids:
            return []
        result = await self.db.execute(
            select(PermissionCondition).where(
                (PermissionCondition.id.in_(ids)),
            )
        )
        permissions = result.scalars().all()
        return [self._to_all_output(p) for p in permissions]

    async def deactivate_by_ids(self, permission_condition_ids: list[UUID]) -> int:
        """Soft-disable conditions by ids. Returns affected row count."""
        if not permission_condition_ids:
            return 0
        result = await self.db.execute(
            update(PermissionCondition)
            .where(PermissionCondition.id.in_(permission_condition_ids))
            .where(PermissionCondition.is_active.is_(True))
            .values(is_active=False)
        )
        return result.rowcount or 0

    async def activate_by_ids(self, permission_condition_ids: list[UUID]) -> int:
        """Re-enable soft-disabled conditions by ids. Returns affected row count."""
        if not permission_condition_ids:
            return 0
        result = await self.db.execute(
            update(PermissionCondition)
            .where(PermissionCondition.id.in_(permission_condition_ids))
            .where(PermissionCondition.is_active.is_(False))
            .values(is_active=True)
        )
        return result.rowcount or 0

    # async def delete_by_permission_ids(self, permission_ids: list[UUID]) -> int:
    #     """Hard-delete all conditions of given permissions. Returns affected row count."""
    #     if not permission_ids:
    #         return 0
    #     result = await self.db.execute(
    #         delete(PermissionCondition).where(PermissionCondition.permission_id.in_(permission_ids))
    #     )
    #     return result.rowcount or 0

    # async def create(self, data: PermissionConditionAllData) -> PermissionConditionAllOutPut:
    #     """Create a new permission condition."""
    #     condition = PermissionCondition(
    #         permission_id=data.permission_id,
    #         type=data.type,
    #         effect=data.effect,
    #         category_id=data.category_id,
    #         media_type_id=data.media_type_id,
    #         role_id=data.role_id,
    #         is_active=data.is_active,
    #     )
    #     self.db.add(condition)
    #     await self.db.flush()
    #     await self.db.refresh(condition)
    #     return PermissionConditionAllOutPut(
    #         id=condition.id,
    #         permission_id=condition.permission_id,
    #         category_id=condition.category_id,
    #         media_type_id=condition.media_type_id,
    #         role_id=condition.role_id,
    #         effect=condition.effect,
    #         type=condition.type,
    #         is_active=condition.is_active,
    #     )
