"""Pydantic schemas for catalog categories.

Pydantic-схемы категорий каталога.
"""

from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema


class CategoryMediaResponse(BaseSchema):
    """Media file metadata.

    Метаданные медиафайла.
    """

    id: UUID
    storage_key: str
    original_filename: str
    mime_type: str
    file_size: int
    width: int | None
    height: int | None
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime


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
    media_data: CategoryMediaResponse | None
