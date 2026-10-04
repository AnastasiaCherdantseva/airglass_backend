"""
Role repository.
"""

from uuid import UUID

from sqlalchemy import Select, select, update

from app.dto import RoleData, RoleOutput, RolePatchData
from app.models.system.role import Role
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.system.role import (
    RoleReadRepositoryProtocol,
    RoleWriteRepositoryProtocol,
)


class RoleRepository(
    BaseIdRepository[Role],
    RoleReadRepositoryProtocol,
    RoleWriteRepositoryProtocol,
):
    model = Role

    def _filter(
        self,
        stmt: Select[tuple[Role]],
        *,
        is_active: bool | None = None,
    ) -> Select[tuple[Role]]:
        if is_active is not None:
            stmt = stmt.where(Role.is_active.is_(is_active))
        return stmt

    def _to_output(self, role: Role) -> RoleOutput:
        return RoleOutput(
            id=role.id,
            name=role.name,
            owner_id=role.owner_id,
            description=role.description,
            is_system=role.is_system,
            is_active=role.is_active,
        )

    async def get_by_owner_id(
        self,
        owner_id: UUID,
        *,
        is_active: bool | None = None,
    ) -> list[RoleOutput]:
        """Роли, созданные указанным владельцем."""
        stmt = select(Role).where(Role.owner_id == owner_id)
        if is_active is not None:
            stmt = self._filter(stmt, is_active=is_active)
        result = await self.db.execute(stmt)
        roles = result.scalars().all()
        return [self._to_output(r) for r in roles]

    async def get_by_ids(self, ids: list[UUID]) -> list[RoleOutput]:
        stmt = select(Role).where(Role.id.in_(ids))
        result = await self.db.execute(stmt)
        roles = result.scalars().all()
        return [self._to_output(r) for r in roles]

    async def create(self, data: RoleData) -> RoleOutput:
        """Создать новую роль."""
        role = Role(
            name=data.name,
            owner_id=data.owner_id,
            description=data.description,
            is_system=data.is_system,
            is_active=data.is_active,
        )
        self.db.add(role)
        await self.db.flush()
        return self._to_output(role)

    async def patch(self, data: RolePatchData) -> RoleOutput | None:
        """Обновить роль. None, если не найдена."""
        role = await self.get_by_id(data.id)
        if role is None:
            return None
        if data.name is not None:
            role.name = data.name
        if data.description is not None:
            role.description = data.description
        if data.is_active is not None:
            role.is_active = data.is_active
        await self.db.flush()
        return self._to_output(role)

    async def activate_by_ids(self, role_ids: list[UUID]) -> int:
        """Активировать неактивные роли. Возвращает rowcount."""
        if not role_ids:
            return 0
        result = await self.db.execute(
            update(Role)
            .where(Role.id.in_(role_ids))
            .where(Role.is_active.is_(False))
            .values(is_active=True)
        )
        return result.rowcount or 0

    async def deactivate_by_ids(self, role_ids: list[UUID]) -> int:
        """Деактивировать активные роли. Возвращает rowcount."""
        if not role_ids:
            return 0
        result = await self.db.execute(
            update(Role)
            .where(Role.id.in_(role_ids))
            .where(Role.is_active.is_(True))
            .values(is_active=False)
        )
        return result.rowcount or 0
