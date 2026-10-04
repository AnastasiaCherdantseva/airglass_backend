"""
Fake-реализация PermissionConditionRepository для юнит-тестов.
"""

from uuid import UUID

from app.dto.system.permission_condition import (
    PermissionConditionAllOutPut,
    PermissionConditionCategoryOutPut,
    PermissionConditionMediaOutPut,
    PermissionConditionRoleOutPut,
)
from app.models.system import (
    ConditionType,
    PermissionCondition,
    PermissionEffect,
)


class FakePermissionConditionRepository:
    """In-memory реализация PermissionConditionRepository."""

    def __init__(
        self,
        conditions: list[PermissionCondition] | None = None,
    ) -> None:
        self.conditions: dict[UUID, PermissionCondition] = {}
        if conditions:
            self.conditions = {c.id: c for c in conditions}

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    def _filter_conditions(
        self,
        conditions: list[PermissionCondition],
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
        condition_type: ConditionType | None = None,
    ) -> list[PermissionCondition]:
        result = conditions
        if is_active is not None:
            result = [c for c in result if c.is_active == is_active]
        if effect is not None:
            result = [c for c in result if c.effect == effect]
        if condition_type is not None:
            result = [c for c in result if c.type == condition_type]
        return result

    async def get_by_role(
        self,
        role_id: UUID,
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
    ) -> list[PermissionConditionRoleOutPut]:
        matched = self._filter_conditions(
            [
                c
                for c in self.conditions.values()
                if c.type == ConditionType.ROLE and c.role_id == role_id
            ],
            is_active=is_active,
            effect=effect,
        )
        return [
            PermissionConditionRoleOutPut(
                id=c.id,
                permission_id=c.permission_id,
                role_id=c.role_id,
                effect=c.effect,
                type=c.type,
                is_active=c.is_active,
            )
            for c in matched
        ]

    async def get_by_category(
        self,
        category_id: UUID,
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
    ) -> list[PermissionConditionCategoryOutPut]:
        matched = self._filter_conditions(
            [
                c
                for c in self.conditions.values()
                if c.type == ConditionType.CATEGORY and c.category_id == category_id
            ],
            is_active=is_active,
            effect=effect,
        )
        return [
            PermissionConditionCategoryOutPut(
                id=c.id,
                permission_id=c.permission_id,
                category_id=c.category_id,
                effect=c.effect,
                type=c.type,
                is_active=c.is_active,
            )
            for c in matched
        ]

    async def get_by_media_type(
        self,
        media_type_id: UUID,
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
    ) -> list[PermissionConditionMediaOutPut]:
        matched = self._filter_conditions(
            [
                c
                for c in self.conditions.values()
                if c.type == ConditionType.MEDIA and c.media_type_id == media_type_id
            ],
            is_active=is_active,
            effect=effect,
        )
        return [
            PermissionConditionMediaOutPut(
                id=c.id,
                permission_id=c.permission_id,
                media_type_id=c.media_type_id,
                effect=c.effect,
                type=c.type,
                is_active=c.is_active,
            )
            for c in matched
        ]

    async def get_by_permission(
        self,
        permission_id: UUID,
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
        condition_type: ConditionType | None = None,
    ) -> list[PermissionConditionAllOutPut]:
        matched = self._filter_conditions(
            [c for c in self.conditions.values() if c.permission_id == permission_id],
            is_active=is_active,
            effect=effect,
            condition_type=condition_type,
        )
        return [self._to_all_output(c) for c in matched]

    async def get_by_ids(self, ids: list[UUID]) -> list[PermissionConditionAllOutPut]:
        if not ids:
            return []
        matched = [c for c in self.conditions.values() if c.id in ids]
        return [self._to_all_output(c) for c in matched]

    @staticmethod
    def _to_all_output(c: PermissionCondition) -> PermissionConditionAllOutPut:
        return PermissionConditionAllOutPut(
            id=c.id,
            permission_id=c.permission_id,
            category_id=c.category_id,
            role_id=c.role_id,
            media_type_id=c.media_type_id,
            effect=c.effect,
            type=c.type,
            is_active=c.is_active,
        )

    # ========================================
    # ЗАПИСЬ
    # ========================================

    async def deactivate_by_ids(self, permission_condition_ids: list[UUID]) -> int:
        if not permission_condition_ids:
            return 0
        count = 0
        for cid in permission_condition_ids:
            c = self.conditions.get(cid)
            if c is not None and c.is_active:
                c.is_active = False
                count += 1
        return count

    async def activate_by_ids(self, permission_condition_ids: list[UUID]) -> int:
        if not permission_condition_ids:
            return 0
        count = 0
        for cid in permission_condition_ids:
            c = self.conditions.get(cid)
            if c is not None and not c.is_active:
                c.is_active = True
                count += 1
        return count

    def add(self, condition: PermissionCondition) -> None:
        self.conditions[condition.id] = condition

    async def delete(self, condition: PermissionCondition) -> None:
        self.conditions.pop(condition.id, None)

    async def flush(self) -> None:
        pass
