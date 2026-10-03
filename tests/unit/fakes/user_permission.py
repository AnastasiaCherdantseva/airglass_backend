"""
Fake-реализация UserPermissionRepository для юнит-тестов.

Составной PK (user_id, condition_id) — ключ tuple.
"""

from uuid import UUID

from app.dto import GroupedPermission
from app.dto.system.permission_condition import PermissionConditionAllOutPut
from app.models.system import Permission, PermissionCondition, UserPermission
from app.models.system.permission import PermissionZone


class FakeUserPermissionRepository:
    """In-memory реализация UserPermissionRepository."""

    def __init__(
        self,
        conditions: dict[UUID, PermissionCondition] | None = None,
        permissions: dict[UUID, Permission] | None = None,
    ) -> None:
        self.links: dict[tuple[UUID, UUID], UserPermission] = {}
        self.conditions = conditions or {}
        self.permissions = permissions or {}

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_grouped_by_permission(
        self,
        user_id: UUID,
    ) -> list[GroupedPermission]:
        grouped: dict[UUID, GroupedPermission] = {}
        for uid, cid in self.links:
            if uid != user_id:
                continue
            condition = self.conditions.get(cid)
            if condition is None:
                continue
            permission = self.permissions.get(condition.permission_id)
            if permission is None:
                continue
            if permission.id not in grouped:
                grouped[permission.id] = GroupedPermission(
                    id=permission.id,
                    code=permission.code,
                    conditions=[],
                )
            grouped[permission.id].conditions.append(
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
        for uid, cid in self.links:
            if uid != user_id:
                continue
            condition = self.conditions.get(cid)
            if condition is None or not condition.is_active:
                continue
            permission = self.permissions.get(condition.permission_id)
            if permission is None:
                continue
            if permission.zone == PermissionZone.ADMIN:
                return True
        return False

    # ========================================
    # ЗАПИСЬ
    # ========================================

    async def replace_for_user(
        self,
        user_id: UUID,
        condition_ids: list[UUID],
    ) -> None:
        # удалить старые связи пользователя
        keys = [k for k in self.links if k[0] == user_id]
        for k in keys:
            del self.links[k]
        # добавить новые
        for cid in condition_ids:
            self.links[(user_id, cid)] = UserPermission(user_id=user_id, condition_id=cid)

    async def delete_by_user_id(self, user_id: UUID) -> int:
        keys = [k for k in self.links if k[0] == user_id]
        for k in keys:
            del self.links[k]
        return len(keys)

    def add(self, link: UserPermission) -> None:
        self.links[(link.user_id, link.condition_id)] = link

    async def delete(self, link: UserPermission) -> None:
        self.links.pop((link.user_id, link.condition_id), None)

    async def flush(self) -> None:
        pass
