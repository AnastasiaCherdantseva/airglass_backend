from dataclasses import dataclass
from uuid import UUID

from pydantic import Field

from app.dto.system.user_permission import GroupedPermission


@dataclass(frozen=True)
class UserData:
    email: str
    name: str
    is_active: bool


@dataclass(frozen=True)
class UserCreate(UserData):
    password: str
    role_ids: list[UUID] = Field(default_factory=list)
    organization_ids: list[UUID] = Field(default_factory=list)


@dataclass(frozen=True)
class UserCreateFull(UserData):
    password_hash: str
    parent_id: UUID


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
    children_count: int


@dataclass(frozen=True)
class UserWithRolesOutput(UserOutput):
    role_ids: list[UUID]


@dataclass(frozen=True)
class CurrentUser(UserOutput):
    permissions: list[GroupedPermission]
    has_admin_access: bool


@dataclass(frozen=True)
class UserListOutput:
    """Обёртка ответа GET /users."""

    items: list[UserWithRolesOutput]
    total: int
    limit: int
    page: int
