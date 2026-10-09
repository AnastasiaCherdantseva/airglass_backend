from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema


class OrganizationCreateRequest(BaseSchema):
    """Схема создания организации."""

    name: str
    inn: str
    address: str | None = None


class OrganizationPatchRequest(BaseSchema):
    """Схема частичного обновления организации."""

    name: str | None = None
    inn: str | None = None
    address: str | None = None


class OrganizationResponse(BaseSchema):
    """Схема ответа с данными организации."""

    id: UUID
    owner_id: UUID
    name: str
    inn: str
    address: str | None
    created_at: datetime
    updated_at: datetime
