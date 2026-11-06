from typing import Protocol

from app.models.suppliers.supplier import Supplier
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class SupplierRepositoryProtocol(
    ReadRepositoryProtocol[Supplier],
    WriteRepositoryProtocol[Supplier],
    Protocol,
):
    """Repository contract for suppliers.

    Контракт репозитория поставщиков.
    """
