from typing import Protocol

from app.models.catalog.material import Material
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class MaterialReadRepositoryProtocol(
    ReadRepositoryProtocol[Material],
    Protocol,
):
    pass


class MaterialWriteRepositoryProtocol(
    WriteRepositoryProtocol[Material],
    Protocol,
):
    pass


class MaterialRepositoryProtocol(
    MaterialReadRepositoryProtocol,
    MaterialWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for materials.

    Контракт репозитория материалов.
    """
