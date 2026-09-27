from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionData:
    name: str
    description: str | None
    code: str
    resource: str | None
    action: str | None
    is_system: bool
