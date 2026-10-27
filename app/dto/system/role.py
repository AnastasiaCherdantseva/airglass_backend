from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.dto.system.permission_condition import PermissionConditionAllOutPut


@dataclass(frozen=True)
class RoleData:
    name: str
    owner_id: UUID | None
    description: str | None
    is_system: bool
    is_active: bool


@dataclass(frozen=True)
class RoleOutput(RoleData):
    id: UUID
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class RoleWithPermissionsOutput(RoleOutput):
    permissions: list[PermissionConditionAllOutPut]


@dataclass(frozen=True)
class RolePatchData:
    id: UUID
    name: str | None
    description: str | None
    is_active: bool | None
