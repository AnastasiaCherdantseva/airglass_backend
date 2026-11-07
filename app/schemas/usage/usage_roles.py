from uuid import UUID

from app.schemas.base import BaseSchema


class UsageRoleResponse(BaseSchema):
    id: UUID
    name: str
    description: str | None
