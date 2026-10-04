"""
Fake-реализация UserRoleRepository для юнит-тестов.

In-memory: хранит связи user ↔ role, не ходит в БД.
Структурно подходит под UserRoleReadRepositoryProtocol и
UserRoleWriteRepositoryProtocol.
"""

from uuid import UUID

from app.dto import (
    RoleOutput,
    UserOutput,
    UserRoleLink,
)
from app.models import Role, User, UserRole


class FakeUserRoleRepository:
    """In-memory реализация UserRoleRepository."""

    def __init__(
        self,
        users: list[User] | None = None,
        roles: list[Role] | None = None,
        links: list[UserRole] | None = None,
    ) -> None:
        self.links: dict[tuple[UUID, UUID], UserRole] = {}
        self.roles: dict[UUID, Role] = {}
        self.users: dict[UUID, User] = {}
        if users:
            self.users = {u.id: u for u in users}
        if roles:
            self.roles = {role.id: role for role in roles}
        if links and roles and users:
            for link in links:
                self.links[(link.user_id, link.role_id)] = link

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_roles_by_user_id(self, user_id: UUID) -> list[RoleOutput]:
        """Найти все роли юзера."""
        result: list[RoleOutput] = []
        for uid, rid in self.links:
            if uid != user_id:
                continue
            role = self.roles.get(rid)
            if role is None or not role.is_active:
                continue
            result.append(
                RoleOutput(
                    id=role.id,
                    name=role.name,
                    description=role.description,
                    is_system=role.is_system,
                    is_active=role.is_active,
                    owner_id=role.owner_id,
                )
            )
        return result

    async def get_users_by_role_id(self, role_id: UUID) -> list[UserOutput]:
        """Найти всех юзеров с ролью."""
        result: list[UserOutput] = []
        for uid, rid in self.links:
            if rid != role_id:
                continue
            user = self.users.get(uid)
            if user is None:
                continue
            if user.deleted_at is not None:
                continue
            result.append(
                UserOutput(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    is_active=user.is_active,
                    parent_id=user.parent_id,
                )
            )
        return result

    # ========================================
    # ЗАПИСЬ
    # ========================================

    def add(self, entity: UserRole) -> None:
        """Добавить связь в память."""
        self.links[entity.user_id, entity.role_id] = entity

    async def delete(self, entity: UserRole) -> None:
        """Удалить связь из памяти."""
        self.links.pop((entity.user_id, entity.role_id), None)

    async def flush(self) -> None:
        """No-op."""
        pass

    async def add_link(self, data: UserRoleLink) -> None:
        """Создать связь."""
        self.links[data.user_id, data.role_id] = UserRole(
            user_id=data.user_id, role_id=data.role_id
        )

    async def add_links(self, links: list[UserRoleLink]) -> None:
        for link in links:
            self.links[(link.user_id, link.role_id)] = UserRole(
                user_id=link.user_id, role_id=link.role_id
            )

    async def remove_link(self, data: UserRoleLink) -> bool:
        key = (data.user_id, data.role_id)
        if key in self.links:
            del self.links[key]
            return True
        return False

    async def remove_links(self, links: list[UserRoleLink]) -> int:
        if not links:
            return 0
        count = 0
        for link in links:
            key = (link.user_id, link.role_id)
            if key in self.links:
                del self.links[key]
                count += 1
        return count

    async def remove_by_user_id(self, user_id: UUID) -> int:
        keys = [k for k in self.links if k[0] == user_id]
        for k in keys:
            del self.links[k]
        return len(keys)

    async def remove_by_role_id(self, role_id: UUID) -> int:
        keys = [k for k in self.links if k[1] == role_id]
        for k in keys:
            del self.links[k]
        return len(keys)
