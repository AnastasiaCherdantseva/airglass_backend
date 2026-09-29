from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RolePermissionLink:
    role_id: UUID
    condition_id: UUID
