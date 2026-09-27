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
        self.users: dict[UUID, User] = {u.id: u for u in (users or [])}
        self.roles: dict[UUID, Role] = {r.id: r for r in (roles or [])}
        self.links: list[UserRole] = list(links or [])

    # ========================================
    # ЧТЕНИЕ
    # ========================================

    async def get_roles_by_user_id(self, user_id: UUID) -> list[RoleOutput]:
        """Найти все роли юзера."""
        result: list[RoleOutput] = []
        for link in self.links:
            if link.user_id != user_id:
                continue
            role = self.roles.get(link.role_id)
            if role is None:
                continue
            if not role.is_active:
                continue
            result.append(
                RoleOutput(
                    id=role.id,
                    name=role.name,
                    description=role.description,
                    is_system=role.is_system,
                    is_active=role.is_active,
                )
            )
        return result

    async def get_users_by_role_id(self, role_id: UUID) -> list[UserOutput]:
        """Найти всех юзеров с ролью."""
        result: list[UserOutput] = []
        for link in self.links:
            if link.role_id != role_id:
                continue
            user = self.users.get(link.user_id)
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
        self.links.append(entity)

    async def delete(self, entity: UserRole) -> None:
        """Удалить связь из памяти."""
        self.links = [
            l
            for l in self.links
            if not (l.user_id == entity.user_id and l.role_id == entity.role_id)
        ]

    async def flush(self) -> None:
        """No-op."""
        pass

    async def add_link(self, data: UserRoleLink) -> None:
        """Создать связь."""
        self.links.append(UserRole(user_id=data.user_id, role_id=data.role_id))

    async def remove_link(self, data: UserRoleLink) -> bool:
        """Удалить связь. True, если была."""
        before = len(self.links)
        self.links = [
            l for l in self.links if not (l.user_id == data.user_id and l.role_id == data.role_id)
        ]
        return len(self.links) < before

    async def remove_by_user_id(self, user_id: UUID) -> int:
        """Удалить все связи юзера."""
        before = len(self.links)
        self.links = [l for l in self.links if l.user_id != user_id]
        return before - len(self.links)

    async def remove_by_role_id(self, role_id: UUID) -> int:
        """Удалить все связи роли."""
        before = len(self.links)
        self.links = [l for l in self.links if l.role_id != role_id]
        return before - len(self.links)
