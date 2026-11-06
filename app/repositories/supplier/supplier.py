from app.models.suppliers.supplier import Supplier
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.suppliers.supplier import (
    SupplierReadRepositoryProtocol,
    SupplierWriteRepositoryProtocol,
)


class SupplierRepository(
    BaseIdRepository[Supplier], SupplierReadRepositoryProtocol, SupplierWriteRepositoryProtocol
):
    """Repository for suppliers.

    Репозиторий поставщиков.
    """

    model = Supplier
