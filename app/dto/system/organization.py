from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class OrganizationData:
    name: str
    inn: str
    address: str | None


@dataclass(frozen=True)
class OrganizationPatch(OrganizationData):
    id: UUID


@dataclass(frozen=True)
class OrganizationOutPut(OrganizationData):
    owner_id: UUID
    id: UUID
