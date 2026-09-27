from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RoleData:
    name: str
    description: str | None
    is_system: bool
    is_active: bool


@dataclass(frozen=True)
class RoleOutput(RoleData):
    id: UUID


@dataclass(frozen=True)
class RolePatchData:
    id: UUID
    name: str | None
    description: str | None
    is_active: bool | None
