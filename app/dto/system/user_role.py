from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserRoleLink:
    user_id: UUID
    role_id: UUID
