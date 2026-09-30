# from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.system.permission import PermissionAction, PermissionResource, PermissionZone

# from decimal import Decimal
from app.schemas.base import BaseSchema
from app.schemas.system.permission_condition import PermissionConditionAll


class PermissionBase(BaseSchema):
    id: UUID
    code: str = Field(min_length=1, max_length=150)


class PermissionFull(PermissionBase):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    resource: PermissionResource
    action: PermissionAction
    zone: PermissionZone


class PermissionWithConditions(PermissionBase):
    conditions: list[PermissionConditionAll]
