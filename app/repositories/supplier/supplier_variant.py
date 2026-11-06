from app.models.suppliers.supplier_variants import SupplierVariant
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.suppliers.supplier_variant import (
    SupplierVariantReadRepositoryProtocol,
    SupplierVariantWriteRepositoryProtocol,
)


class SupplierVariantRepository(
    BaseIdRepository[SupplierVariant],
    SupplierVariantReadRepositoryProtocol,
    SupplierVariantWriteRepositoryProtocol,
):
    """Repository for supplier product variants.

    Репозиторий предложений поставщиков.
    """

    model = SupplierVariant
