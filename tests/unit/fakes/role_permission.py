"""
Fake-реализация RolePermissionRepository для юнит-тестов.

Составной PK (role_id, condition_id) — ключ tuple.
"""

from uuid import UUID

from app.dto.system.permission_condition import PermissionConditionAllOutPut
from app.dto.system.user_permission import GroupedPermission
from app.models import Permission, PermissionCondition, Role, RolePermission


class FakeRolePermissionRepository:
    """In-memory реализация RolePermissionRepository."""

    def __init__(
        self,
        *,
        roles: list[Role] | None = None,
        permissions: list[Permission] | None = None,
        conditions: list[PermissionCondition] | None = None,
        links: list[RolePermission] | None = None,
    ) -> None:
        self.links: dict[tuple[UUID, UUID], RolePermission] = {}
        self.roles: dict[UUID, Role] = {}
        self.permissions: dict[UUID, Permission] = {}
        self.conditions: dict[UUID, PermissionCondition] = {}
        if roles:
            self.roles = {role.id: role for role in roles}
        if permissions:
            self.permissions = {p.id: p for p in permissions}
        if conditions:
            self.conditions = {c.id: c for c in conditions}
        if links and roles and conditions:
            for link in links:
                self.links[(link.role_id, link.condition_id)] = link

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_condition_ids_by_role_id(self, role_id: UUID) -> list[UUID]:
        return [cid for (rid, cid) in self.links if rid == role_id]

    async def get_role_ids_by_condition_id(self, condition_id: UUID) -> list[UUID]:
        return [rid for (rid, cid) in self.links if cid == condition_id]

    async def get_conditions_by_role_ids(
        self,
        role_ids: list[UUID],
    ) -> dict[UUID, list[GroupedPermission]]:
        """Return grouped permissions per role id.

        Возвращает сгруппированные права по идентификатору роли.
        """
        requested_role_ids = set(role_ids)
        grouped: dict[UUID, dict[UUID, GroupedPermission]] = {}

        for role_id, condition_id in self.links:
            if role_id not in requested_role_ids:
                continue

            condition = self.conditions.get(condition_id)
            if condition is None:
                continue

            permission = self.permissions.get(condition.permission_id)
            if permission is None:
                continue

            role_group = grouped.setdefault(role_id, {})
            if permission.id not in role_group:
                role_group[permission.id] = GroupedPermission(
                    id=permission.id,
                    code=permission.code,
                    conditions=[],
                )
            role_group[permission.id].conditions.append(
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

        return {role_id: list(g.values()) for role_id, g in grouped.items()}
