"""
Protocols for the users repos.
"""

from typing import Protocol
from uuid import UUID

from app.repositories.protocols.dto import (
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


class UserRoleWriteRepositoryProtocol(Protocol):
    async def add_link(self, data: UserRoleLink) -> None: ...

    async def remove_link(self, data: UserRoleLink) -> bool: ...

    async def remove_by_user_id(self, user_id: UUID) -> int: ...

    async def remove_by_role_id(self, role_id: UUID) -> int: ...
