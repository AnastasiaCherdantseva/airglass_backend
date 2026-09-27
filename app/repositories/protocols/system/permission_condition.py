from typing import Protocol
from uuid import UUID

from app.models import PermissionCondition
from app.repositories.protocols import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)
from app.repositories.protocols.dto import (
    PermissionConditionAllData,
    PermissionConditionAllOutPut,
    PermissionConditionCategoryOutPut,
    PermissionConditionRoleOutPut,
)


class PermissionConditionReadRepositoryProtocol(
    ReadRepositoryProtocol[PermissionCondition], Protocol
):
    """Read Permissions."""

    async def get_by_role(self, role_id: UUID) -> list[PermissionConditionRoleOutPut]: ...

    async def get_by_category(
        self, category_id: UUID
    ) -> list[PermissionConditionCategoryOutPut]: ...

    async def get_by_permission(
        self, permission_id: UUID
    ) -> list[PermissionConditionAllOutPut]: ...

    async def get_by_user(self, user_id: UUID) -> list[PermissionConditionAllOutPut]: ...


class PermissionConditionWriteRepositoryProtocol(
    WriteRepositoryProtocol[PermissionCondition], Protocol
):
    """Write Permissions."""

    async def deactivate_by_ids(self, permission_condition_ids: list[UUID]) -> int: ...
    async def activate_by_ids(self, permission_condition_ids: list[UUID]) -> int: ...
    async def delete_by_permission_ids(self, permission_ids: list[UUID]) -> int: ...
    async def create(self, data: PermissionConditionAllData) -> PermissionConditionAllOutPut: ...
