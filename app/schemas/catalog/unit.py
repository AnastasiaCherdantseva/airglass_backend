from uuid import UUID

from app.schemas.base import BaseSchema


class UnitResponse(BaseSchema):
    id: UUID
    name: str
    symbol: str
