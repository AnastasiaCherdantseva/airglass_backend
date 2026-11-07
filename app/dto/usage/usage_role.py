from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UsageRoleOutput:
    id: UUID
    name: str
    description: str | None
