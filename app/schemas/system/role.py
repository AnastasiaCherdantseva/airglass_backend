"""
Pydantic-схемы для ролей
"""

from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema
from app.schemas.system.permission import PermissionWithConditions

# ============================================================
# ROLE
# ============================================================


class RoleBase(BaseSchema):
    """Базовые поля роли."""

    name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(None, max_length=1000)
    is_active: bool = True
    owner_id: UUID | None


class RoleCreateRequest(BaseSchema):
    """Создание роли."""

    name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(None, max_length=1000)
    is_active: bool = True
    condition_ids: list[UUID] = Field(
        default_factory=list,
        min_length=1,
    )

    @field_validator("condition_ids")
    @classmethod
    def _dedupe_condition_ids(cls, value: list[UUID]) -> list[UUID]:
        return list(dict.fromkeys(value))


class RoleUpdate(BaseSchema):
    """Обновление роли. Все поля опциональны."""

    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = Field(None, max_length=1000)
    is_active: bool | None = None


class RoleResponse(RoleBase):
    """Полный ответ по роли."""

    id: UUID
    is_system: bool


class RoleDetailResponse(RoleResponse):
    permissions: list[PermissionWithConditions]
    created_at: datetime
    updated_at: datetime
