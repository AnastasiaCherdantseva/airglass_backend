"""
Fake-реализация RolePermissionRepository для юнит-тестов.

Составной PK (role_id, condition_id) — ключ tuple.
"""

from uuid import UUID

from app.models.system import RolePermission


class FakeRolePermissionRepository:
    """In-memory реализация RolePermissionRepository."""

    def __init__(self, initial: list[RolePermission] | None = None) -> None:
        self.links: dict[tuple[UUID, UUID], RolePermission] = {}
        if initial:
            for link in initial:
                self.links[(link.role_id, link.condition_id)] = link

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_condition_ids_by_role_id(self, role_id: UUID) -> list[UUID]:
        return [cid for (rid, cid) in self.links if rid == role_id]

    async def get_role_ids_by_condition_id(self, condition_id: UUID) -> list[UUID]:
        return [rid for (rid, cid) in self.links if cid == condition_id]
