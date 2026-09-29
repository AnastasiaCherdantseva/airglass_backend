from dataclasses import dataclass
from uuid import UUID

from app.dto.system.permission_condition import PermissionConditionAllOutPut


@dataclass(frozen=True)
class UserPermissionLink:
    user_id: UUID
    permission_id: UUID


@dataclass(frozen=True)
class GroupedPermission:
    """Permission с метаданными и списком условий пользователя."""

    permission_id: UUID
    code: str
    conditions: list[PermissionConditionAllOutPut]
