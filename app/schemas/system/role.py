"""
Pydantic-схемы для ролей
"""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema


# ============================================================
# ROLE
# ============================================================

class RoleBase(BaseSchema):
    """Базовые поля роли."""
    code: str = Field(min_length=2, max_length=50)
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


class RoleShort(BaseSchema):
    """Краткая схема роли — для вложенного использования."""
    id: UUID
    code: str
    name: str


class RoleResponse(RoleBase):
    """Полный ответ по роли."""
    id: UUID
    is_system: bool
    created_at: datetime
    updated_at: datetime
