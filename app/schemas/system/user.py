# from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import Field

# from decimal import Decimal
from app.schemas.base import BaseSchema, Email
from app.schemas.system.role import RoleShort


class UserBase(BaseSchema):
    name: str = Field(min_length=2, max_length=255)
    email: Email = Field(min_length=6, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    role_ids: list[UUID] = Field(default_factory=list)


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
    roles: list[RoleShort] = Field(default_factory=list)
    is_active: bool
    created_at: datetime
    updated_at: datetime
