from typing import Protocol

from app.models.catalog.material_group import MaterialGroup
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class MaterialGroupRepositoryProtocol(
    ReadRepositoryProtocol[MaterialGroup],
    WriteRepositoryProtocol[MaterialGroup],
    Protocol,
):
    """Repository contract for material groups.

    Контракт репозитория групп материалов.
    """
