from typing import Protocol

from app.models.catalog.material_group import MaterialGroup
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class MaterialGroupReadRepositoryProtocol(
    ReadRepositoryProtocol[MaterialGroup],
    Protocol,
):
    pass


class MaterialGroupWriteRepositoryProtocol(
    WriteRepositoryProtocol[MaterialGroup],
    Protocol,
):
    pass


class MaterialGroupRepositoryProtocol(
    MaterialGroupReadRepositoryProtocol,
    MaterialGroupWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for material groups.

    Контракт репозитория групп материалов.
    """
