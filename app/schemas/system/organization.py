from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.dto.system.organization import OrganizationOutPut
from app.schemas.base import BaseSchema


class OrganizationCreateRequest(BaseSchema):
    """Схема создания организации."""

    name: str = Field(
        min_length=1,
        max_length=255,
    )
    inn: str = Field(pattern=r"^\d{12}$")
    address: str | None = None


class OrganizationPatchSchema(BaseSchema):
    """Схема частичного обновления организации."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    inn: str | None = Field(default=None, pattern=r"^\d{12}$")
    address: str | None = None


class OrganizationResponse(BaseSchema):
    """Схема ответа с данными организации."""

    id: UUID
    owner_id: UUID
    name: str
    inn: str = Field(pattern=r"^\d{12}$")
    address: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, org: OrganizationOutPut) -> "OrganizationResponse":
        return cls(
            id=org.id,
            owner_id=org.owner_id,
            name=org.name,
            inn=org.inn,
            address=org.address,
            created_at=org.created_at,
            updated_at=org.updated_at,
        )
