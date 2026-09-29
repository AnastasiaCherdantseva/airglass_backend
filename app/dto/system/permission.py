from dataclasses import dataclass
from typing import Literal
from uuid import UUID


@dataclass(frozen=True)
class PermissionData:
    name: str
    description: str | None
    code: str
    resource: str | None
    action: str | None
    zone: Literal["admin", "public"]


@dataclass(frozen=True)
class PermissionOutput(PermissionData):
    id: UUID
