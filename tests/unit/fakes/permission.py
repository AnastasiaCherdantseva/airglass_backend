"""
Fake-реализация PermissionRepository для юнит-тестов.

In-memory: хранит permissions в словаре, не ходит в БД.
Структурно подходит под PermissionRepositoryProtocol.
"""

from uuid import UUID

from app.dto.system.permission import PermissionOutput
from app.models.system import Permission


class FakePermissionRepository:
    """In-memory реализация PermissionRepository."""

    def __init__(self, initial: list[Permission] | None = None) -> None:
        self.permissions: dict[UUID, Permission] = {}
        if initial:
            for p in initial:
                self.permissions[p.id] = p

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_by_code(self, code: str) -> PermissionOutput | None:
        """Найти permission по code."""
        p = next(
            (p for p in self.permissions.values() if p.code == code),
            None,
        )
        if p is None:
            return None
        return PermissionOutput(
            id=p.id,
            code=p.code,
            resource=p.resource,
            action=p.action,
            zone=p.zone,
            name=p.name,
            description=p.description,
        )
