"""
UserRole repository — link between users and roles.
"""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.system import (
    RoleOutput,
    UserOutput,
    UserRoleLink,
)
from app.models.system.role import Role
from app.models.system.user import User
from app.models.system.user_role import UserRole
from app.repositories.protocols.system.user_role import (
    UserRoleReadRepositoryProtocol,
    UserRoleWriteRepositoryProtocol,
)


class UserRoleRepository(
    UserRoleReadRepositoryProtocol,
    UserRoleWriteRepositoryProtocol,
):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def add(self, entity: UserRole) -> None:
        self.db.add(entity)

    async def delete(self, entity: UserRole) -> None:
        await self.db.delete(entity)

    async def flush(self) -> None:
        await self.db.flush()

    async def get_roles_by_user_id(self, user_id: UUID) -> list[RoleOutput]:
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                Role.is_active.is_(True),
            )
        )
        result = await self.db.execute(stmt)
        return [
            RoleOutput(
                id=row.id,
                name=row.name,
                is_system=row.is_system,
                is_active=row.is_active,
                description=row.description,
            )
            for row in result.all()
        ]

    async def get_users_by_role_id(self, role_id: UUID) -> list[UserOutput]:
        stmt = (
            select(User)
            .join(UserRole, UserRole.user_id == User.id)
            .where(
                UserRole.role_id == role_id,
                User.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return [
            UserOutput(
                id=row.id,
                name=row.name,
                email=row.email,
                is_active=row.is_active,
                parent_id=row.parent_id,
            )
            for row in result.all()
        ]

    async def add_link(self, data: UserRoleLink) -> None:
        link = UserRole(
            user_id=data.user_id,
            role_id=data.role_id,
        )
        self.db.add(link)
        await self.db.flush()

    async def remove_link(self, data: UserRoleLink) -> bool:
        stmt = delete(UserRole).where(
            UserRole.user_id == data.user_id,
            UserRole.role_id == data.role_id,
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount > 0

    async def remove_by_user_id(self, user_id: UUID) -> int:
        stmt = delete(UserRole).where(UserRole.user_id == user_id)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount

    async def remove_by_role_id(self, role_id: UUID) -> int:
        stmt = delete(UserRole).where(UserRole.role_id == role_id)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount
