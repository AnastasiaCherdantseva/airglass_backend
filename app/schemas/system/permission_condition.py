# from typing import Optional
from uuid import UUID

from app.models.system.permission_condition import ConditionType, PermissionEffect

# from decimal import Decimal
from app.schemas.base import BaseSchema


class PermissionConditionBase(BaseSchema):
    id: UUID
    permission_id: UUID
    type: ConditionType
    effect: PermissionEffect
    is_active: bool


class PermissionConditionAll(PermissionConditionBase):
    category_id: UUID | None
    media_type_id: UUID | None
    role_id: UUID | None


class PermissionConditionCategory(PermissionConditionBase):
    category_id: UUID


class PermissionConditionMediaType(PermissionConditionBase):
    media_type_id: UUID


class PermissionConditionRole(PermissionConditionBase):
    role_id: UUID
