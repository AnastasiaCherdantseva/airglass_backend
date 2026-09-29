from typing import Protocol
from uuid import UUID

from app.dto import GroupedPermission


class UserPermissionReadRepositoryProtocol(Protocol):
    """UserPermission — read."""

    async def get_grouped_by_permission(
        self,
        user_id: UUID,
    ) -> list[GroupedPermission]: ...

    # async def get_users_by_condition_id(self, condition_id: UUID) -> list[UserOutput]: ...

    # async def get_condition_ids_by_user_id(
    #     self,
    #     user_id: UUID,
    # ) -> list[UUID]: ...


class UserPermissionWriteRepositoryProtocol(Protocol):
    """UserPermission — write."""

    async def replace_for_user(
        self,
        user_id: UUID,
        condition_ids: list[UUID],
    ) -> None: ...

    async def delete_by_user_id(self, user_id: UUID) -> int: ...


class UserPermissionRepositoryProtocol(
    UserPermissionReadRepositoryProtocol,
    UserPermissionWriteRepositoryProtocol,
    Protocol,
):
    """Full UserPermission repository."""

    pass
