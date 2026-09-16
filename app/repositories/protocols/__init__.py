# app/repositories/protocols/__init__.py
"""
Protocol-контракты для репозиториев.
"""

from app.repositories.protocols.base import (
    ReadRepositoryProtocol,
    WriteRepositoryProtocol,
)
from app.repositories.protocols.user import (
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