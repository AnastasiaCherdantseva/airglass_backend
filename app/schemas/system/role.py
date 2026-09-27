"""
Pydantic-схемы для ролей
"""

from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from app.schemas.base import BaseSchema

# ============================================================
# ROLE
# ============================================================


class RoleBase(BaseSchema):
    """Базовые поля роли."""

    name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(None, max_length=1000)
    is_active: bool = True


class RoleCreate(RoleBase):
    """Создание роли."""

    is_system: bool = False


class RoleUpdate(BaseSchema):
    """Обновление роли. Все поля опциональны."""

    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = Field(None, max_length=1000)
    is_active: bool | None = None


class RoleResponse(RoleBase):
    """Полный ответ по роли."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    is_system: bool


class RoleDetailResponse(RoleResponse):
    created_at: datetime
    updated_at: datetime
