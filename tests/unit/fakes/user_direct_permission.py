"""
Fake-реализация UserDirectPermissionRepository для юнит-тестов.

Составной PK (user_id, condition_id) — ключ tuple.
"""

from uuid import UUID

from app.models.system import UserDirectPermission


class FakeUserDirectPermissionRepository:
    """In-memory реализация UserDirectPermissionRepository."""

    def __init__(self, initial: list[UserDirectPermission] | None = None) -> None:
        self.links: dict[tuple[UUID, UUID], UserDirectPermission] = {}
        if initial:
            for link in initial:
                self.links[(link.user_id, link.condition_id)] = link

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_condition_ids_by_user_id(self, user_id: UUID) -> list[UUID]:
        return [cid for (uid, cid) in self.links if uid == user_id]

    async def get_user_ids_by_condition_id(self, condition_id: UUID) -> list[UUID]:
        return [uid for (uid, cid) in self.links if cid == condition_id]
