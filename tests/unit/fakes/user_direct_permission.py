"""
Fake-реализация UserDirectPermissionRepository для юнит-тестов.

Составной PK (user_id, condition_id) — ключ tuple.
"""

from uuid import UUID

from app.models.system import User, UserDirectPermission
from app.models.system.permission_condition import PermissionCondition


class FakeUserDirectPermissionRepository:
    """In-memory реализация UserDirectPermissionRepository."""

    def __init__(
        self,
        users: list[User] | None = None,
        conditions: list[PermissionCondition] | None = None,
        links: list[UserDirectPermission] | None = None,
    ) -> None:
        self.links: dict[tuple[UUID, UUID], UserDirectPermission] = {}
        self.conditions: dict[UUID, PermissionCondition] = {}
        self.users: dict[UUID, User] = {}
        if conditions:
            self.users = {c.id: c for c in conditions}
        if users:
            self.users = {user.id: user for user in users}
        if links and users and conditions:
            for link in links:
                self.links[(link.user_id, link.condition_id)] = link

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_condition_ids_by_user_id(self, user_id: UUID) -> list[UUID]:
        return [cid for (uid, cid) in self.links if uid == user_id]

    async def get_user_ids_by_condition_id(self, condition_id: UUID) -> list[UUID]:
        return [uid for (uid, cid) in self.links if cid == condition_id]
