from app.repositories.protocols.base import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)
from app.repositories.protocols.system.user import (
    UserReadRepositoryProtocol,
    UserWriteRepositoryProtocol,
)

# from app.repositories.protocols.role import (
#     RoleReadRepositoryProtocol,
#     RoleWriteRepositoryProtocol,
# )

__all__ = [
    "ReadRepositoryProtocol",
    "WriteRepositoryProtocol",
    "UserReadRepositoryProtocol",
    "UserWriteRepositoryProtocol",
    # "RoleReadRepositoryProtocol",
    # "RoleWriteRepositoryProtocol",
]
