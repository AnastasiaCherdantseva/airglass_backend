from app.repositories.protocols.system.organization import (
    OrganizationReadRepositoryProtocol,
    OrganizationWriteRepositoryProtocol,
)
from app.repositories.protocols.system.permission import (
    PermissionReadRepositoryProtocol,
    PermissionWriteRepositoryProtocol,
)
from app.repositories.protocols.system.permission_condition import (
    PermissionConditionReadRepositoryProtocol,
    PermissionConditionWriteRepositoryProtocol,
)
from app.repositories.protocols.system.role import (
    RoleReadRepositoryProtocol,
    RoleWriteRepositoryProtocol,
)
from app.repositories.protocols.system.role_permission import (
    RolePermissionReadRepositoryProtocol,
    RolePermissionWriteRepositoryProtocol,
)
from app.repositories.protocols.system.session import (
    SessionReadRepositoryProtocol,
    SessionRepositoryProtocol,
    SessionWriteRepositoryProtocol,
)
from app.repositories.protocols.system.user import (
    UserReadRepositoryProtocol,
    UserRepositoryProtocol,
    UserWriteRepositoryProtocol,
)
from app.repositories.protocols.system.user_direct_permission import (
    UserDirectPermissionReadRepositoryProtocol,
    UserDirectPermissionRepositoryProtocol,
    UserDirectPermissionWriteRepositoryProtocol,
)
from app.repositories.protocols.system.user_organization import (
    UserOrganizationReadRepositoryProtocol,
    UserOrganizationRepositoryProtocol,
    UserOrganizationWriteRepositoryProtocol,
)
from app.repositories.protocols.system.user_permission import (
    UserPermissionReadRepositoryProtocol,
    UserPermissionRepositoryProtocol,
    UserPermissionWriteRepositoryProtocol,
)
from app.repositories.protocols.system.user_role import (
    UserRoleReadRepositoryProtocol,
    UserRoleWriteRepositoryProtocol,
)

__all__ = [
    "SessionReadRepositoryProtocol",
    "SessionWriteRepositoryProtocol",
    "SessionRepositoryProtocol",
    "UserReadRepositoryProtocol",
    "UserWriteRepositoryProtocol",
    "UserRepositoryProtocol",
    #
    "OrganizationReadRepositoryProtocol",
    "OrganizationWriteRepositoryProtocol",
    #
    "PermissionReadRepositoryProtocol",
    "PermissionWriteRepositoryProtocol",
    "PermissionConditionReadRepositoryProtocol",
    "PermissionConditionWriteRepositoryProtocol",
    "RolePermissionReadRepositoryProtocol",
    "RolePermissionWriteRepositoryProtocol",
    "RoleReadRepositoryProtocol",
    "RoleWriteRepositoryProtocol",
    "UserPermissionReadRepositoryProtocol",
    "UserPermissionWriteRepositoryProtocol",
    "UserPermissionRepositoryProtocol",
    #
    "UserRoleReadRepositoryProtocol",
    "UserRoleWriteRepositoryProtocol",
    #
    "UserDirectPermissionReadRepositoryProtocol",
    "UserDirectPermissionWriteRepositoryProtocol",
    "UserDirectPermissionRepositoryProtocol",
    #
    "UserOrganizationReadRepositoryProtocol",
    "UserOrganizationWriteRepositoryProtocol",
    "UserOrganizationRepositoryProtocol",
]
