from typing import Protocol

from app.models.catalog.material import Material
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class MaterialRepositoryProtocol(
    ReadRepositoryProtocol[Material],
    WriteRepositoryProtocol[Material],
    Protocol,
):
    """Repository contract for materials.

    Контракт репозитория материалов.
    """
