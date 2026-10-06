# from typing import Optional
from uuid import UUID

from pydantic import Field, field_validator

# from decimal import Decimal
from app.schemas.base import BaseSchema, Email
from app.schemas.system.permission import PermissionWithConditions


class UserBase(BaseSchema):
    name: str = Field(min_length=2, max_length=255)
    email: Email = Field(min_length=6, max_length=255)


class UserCreateRequest(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    role_ids: list[UUID] = Field(min_length=1)

    @field_validator("role_ids")
    @classmethod
    def _dedupe_role_ids(cls, value: list[UUID]) -> list[UUID]:
        """
        Remove duplicate role ids, keep order.

        Убирает дубли id ролей, порядок сохраняется.
        """
        return list(dict.fromkeys(value))


class UserUpdate(BaseSchema):
    """Обновление."""

    name: str | None = Field(None, min_length=1, max_length=255)
    email: Email | None = None
    # [] - снять все роли, None - не трогать роли вообще
    role_ids: list[UUID] | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    """Ответ."""

    id: UUID


class UserWithChildrenResponse(UserResponse):
    children_count: int = Field(ge=0)


class UserWithRolesResponse(UserResponse):
    is_active: bool
    parent_id: UUID | None
    role_ids: list[UUID]


class MeResponse(UserBase):
    """Ответ."""

    is_active: bool
    id: UUID
    has_admin_access: bool
    permissions: list[PermissionWithConditions]


class meUsersListItem(UserWithChildrenResponse, UserWithRolesResponse):
    pass


class meUsers(BaseSchema):
    items: list[meUsersListItem]
    limit: int
    total: int
    page: int
