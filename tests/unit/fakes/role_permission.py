"""
Fake-реализация RolePermissionRepository для юнит-тестов.

Составной PK (role_id, condition_id) — ключ tuple.
"""

from uuid import UUID

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
