from typing import Protocol

from app.models.suppliers.supplier import Supplier
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class SupplierReadRepositoryProtocol(
    ReadRepositoryProtocol[Supplier],
    Protocol,
):
    pass


class SupplierWriteRepositoryProtocol(
    WriteRepositoryProtocol[Supplier],
    Protocol,
):
    pass


class SupplierRepositoryProtocol(
    SupplierReadRepositoryProtocol,
    SupplierWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for suppliers.

    Контракт репозитория поставщиков.
    """
