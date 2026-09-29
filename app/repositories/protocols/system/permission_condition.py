from typing import Protocol
from uuid import UUID

from app.dto import (
    PermissionConditionAllOutPut,
    PermissionConditionCategoryOutPut,
    PermissionConditionMediaOutPut,
    PermissionConditionRoleOutPut,
)
from app.models import ConditionType, PermissionCondition, PermissionEffect
from app.repositories.protocols import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)


class PermissionConditionReadRepositoryProtocol(
    ReadRepositoryProtocol[PermissionCondition], Protocol
):
    """Read Permissions."""

    async def get_by_role(
        self,
        role_id: UUID,
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
    ) -> list[PermissionConditionRoleOutPut]: ...

    async def get_by_category(
        self,
        category_id: UUID,
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
    ) -> list[PermissionConditionCategoryOutPut]: ...
    async def get_by_media_type(
        self,
        media_type_id: UUID,
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
    ) -> list[PermissionConditionMediaOutPut]: ...

    async def get_by_permission(
        self,
        permission_id: UUID,
        *,
        is_active: bool | None = None,
        effect: PermissionEffect | None = None,
        condition_type: ConditionType | None = None,
    ) -> list[PermissionConditionAllOutPut]: ...

    async def get_by_ids(self, ids: list[UUID]) -> list[PermissionConditionAllOutPut]: ...


class PermissionConditionWriteRepositoryProtocol(
    WriteRepositoryProtocol[PermissionCondition], Protocol
):
    """Write Permissions."""

    async def deactivate_by_ids(self, permission_condition_ids: list[UUID]) -> int: ...
    async def activate_by_ids(self, permission_condition_ids: list[UUID]) -> int: ...

    # async def delete_by_permission_ids(self, permission_ids: list[UUID]) -> int: ...

    # async def create(self, data: PermissionConditionAllData) -> PermissionConditionAllOutPut: ...
