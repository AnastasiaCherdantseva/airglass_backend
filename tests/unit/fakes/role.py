"""
Fake-реализация RoleRepository для юнит-тестов.
"""

from uuid import UUID

from app.dto.system.role import RoleData, RoleOutput, RolePatchData
from app.models.system import Role


class FakeRoleRepository:
    """In-memory реализация RoleRepository."""

    def __init__(self, initial: list[Role] | None = None) -> None:
        self.roles: dict[UUID, Role] = {}
        if initial:
            for r in initial:
                self.roles[r.id] = r

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_by_id(self, role_id: UUID) -> Role | None:
        return self.roles.get(role_id)

    async def get_by_owner_id(
        self,
        owner_id: UUID,
        *,
        is_active: bool | None = None,
    ) -> list[RoleOutput]:
        matched = [r for r in self.roles.values() if r.owner_id == owner_id]
        if is_active is not None:
            matched = [r for r in matched if r.is_active == is_active]
        return [self._to_output(r) for r in matched]

    # ========================================
    # ЗАПИСЬ
    # ========================================

    async def create(self, data: RoleData) -> RoleOutput:
        from uuid import uuid4

        role = Role(
            id=uuid4(),
            name=data.name,
            owner_id=data.owner_id,
            description=data.description,
            is_system=data.is_system,
            is_active=data.is_active,
        )
        self.roles[role.id] = role
        return self._to_output(role)

    async def patch(self, data: RolePatchData) -> RoleOutput | None:
        role = self.roles.get(data.id)
        if role is None:
            return None
        if data.name is not None:
            role.name = data.name
        if data.description is not None:
            role.description = data.description
        if data.is_active is not None:
            role.is_active = data.is_active
        return self._to_output(role)

    async def activate_by_ids(self, role_ids: list[UUID]) -> int:
        if not role_ids:
            return 0
        count = 0
        for rid in role_ids:
            r = self.roles.get(rid)
            if r is not None and not r.is_active:
                r.is_active = True
                count += 1
        return count

    async def deactivate_by_ids(self, role_ids: list[UUID]) -> int:
        if not role_ids:
            return 0
        count = 0
        for rid in role_ids:
            r = self.roles.get(rid)
            if r is not None and r.is_active:
                r.is_active = False
                count += 1
        return count

    def add(self, role: Role) -> None:
        self.roles[role.id] = role

    async def delete(self, role: Role) -> None:
        self.roles.pop(role.id, None)

    async def flush(self) -> None:
        pass

    @staticmethod
    def _to_output(r: Role) -> RoleOutput:
        return RoleOutput(
            id=r.id,
            name=r.name,
            owner_id=r.owner_id,
            description=r.description,
            is_system=r.is_system,
            is_active=r.is_active,
        )
