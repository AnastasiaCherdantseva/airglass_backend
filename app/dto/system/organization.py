from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class OrganizationData:
    name: str
    inn: str
    address: str | None


@dataclass(frozen=True)
class OrganizationPatch:
    id: UUID
    name: str | None = None
    inn: str | None = None
    address: str | None = None


@dataclass(frozen=True)
class OrganizationOutPut(OrganizationData):
    owner_id: UUID
    id: UUID
    created_at: datetime
    updated_at: datetime
