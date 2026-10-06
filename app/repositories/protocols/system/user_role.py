"""
Protocols for the users repos.
"""

from typing import Protocol
from uuid import UUID

from app.dto import (
    RoleOutput,
    UserOutput,
    UserRoleLink,
)


class UserRoleReadRepositoryProtocol(Protocol):
    async def get_roles_by_user_id(
        self,
        user_id: UUID,
    ) -> list[RoleOutput]: ...

    async def get_users_by_role_id(
        self,
        role_id: UUID,
    ) -> list[UserOutput]: ...
    async def get_user_ids_by_role_id(self, role_id: UUID) -> list[UUID]: ...
    async def get_role_ids_by_user_ids(
        self,
        user_ids: list[UUID],
    ) -> dict[UUID, list[UUID]]: ...

    """
    Вернуть {user_id: [role_id, ...]} для указанных user_ids.

    Контракт: возвращаются ТОЛЬКО ключи из user_ids.
    Если у user нет ролей — его не будет в словаре.
    """


class UserRoleWriteRepositoryProtocol(Protocol):
    async def add_link(self, data: UserRoleLink) -> None: ...
    async def add_links(self, links: list[UserRoleLink]) -> None: ...

    async def remove_link(self, data: UserRoleLink) -> bool: ...
    async def remove_links(self, links: list[UserRoleLink]) -> int: ...

    async def remove_by_user_id(self, user_id: UUID) -> int: ...

    async def remove_by_role_id(self, role_id: UUID) -> int: ...


class UserRoleRepositoryProtocol(
    UserRoleWriteRepositoryProtocol,
    UserRoleReadRepositoryProtocol,
    Protocol,
):
    """Full UserPermission repository."""

    pass
