from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class PermissionData:
    name: str
    description: str | None
    code: str
    resource: str | None
    action: str | None
    is_system: bool


@dataclass(frozen=True)
class PermissionOutput(PermissionData):
    id: UUID
