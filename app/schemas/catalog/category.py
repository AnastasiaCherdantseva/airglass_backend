"""Pydantic schemas for catalog categories.

Pydantic-схемы категорий каталога.
"""

from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema
from app.schemas.media.media_file import MediaFileResponse


class CategoryResponse(BaseSchema):
    """Category response with related attributes, usage roles and media.

    Ответ с категорией, связанными атрибутами, ролями использования и медиафайлом.
    """

    id: UUID
    parent_id: UUID | None
    name: str
    code: str
    description: str | None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    attributes_ids: list[UUID]
    usage_role_ids: list[UUID]
    media_data: MediaFileResponse | None
