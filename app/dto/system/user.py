from dataclasses import dataclass
from uuid import UUID

from app.dto.system.user_permission import GroupedPermission


@dataclass(frozen=True)
class UserData:
    email: str
    name: str
    is_active: bool


@dataclass(frozen=True)
class UserPatchInput:
    id: UUID
    email: str | None
    name: str | None
    new_password_hash: str | None


@dataclass(frozen=True)
class UserOutput(UserData):
    id: UUID
    parent_id: UUID | None


@dataclass(frozen=True)
class CurrentUserOutput(UserOutput):
    permissions: list[GroupedPermission]
    has_admin_access: bool
