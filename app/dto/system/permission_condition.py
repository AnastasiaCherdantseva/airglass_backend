from dataclasses import dataclass
from uuid import UUID

from app.models.system.permission_condition import ConditionType, PermissionEffect


@dataclass(frozen=True)
class PermissionConditionData:
    permission_id: UUID
    is_active: bool
    effect: PermissionEffect
    type: ConditionType


@dataclass(frozen=True)
class PermissionConditionRoleData(PermissionConditionData):
    role_id: UUID


@dataclass(frozen=True)
class PermissionConditionCategoryData(PermissionConditionData):
    category_id: UUID


@dataclass(frozen=True)
class PermissionConditionMediaData(PermissionConditionData):
    media_type_id: UUID


@dataclass(frozen=True)
class PermissionConditionAllData(PermissionConditionData):
    category_id: UUID | None
    role_id: UUID | None
    media_type_id: UUID | None


@dataclass(frozen=True)
class PermissionConditionOutPut(PermissionConditionData):
    id: UUID | None


@dataclass(frozen=True)
class PermissionConditionRoleOutPut(PermissionConditionOutPut):
    role_id: UUID


@dataclass(frozen=True)
class PermissionConditionCategoryOutPut(PermissionConditionOutPut):
    category_id: UUID


@dataclass(frozen=True)
class PermissionConditionMediaOutPut(PermissionConditionOutPut):
    media_type_id: UUID


@dataclass(frozen=True)
class PermissionConditionAllOutPut(PermissionConditionOutPut):
    category_id: UUID | None
    role_id: UUID | None
    media_type_id: UUID | None
