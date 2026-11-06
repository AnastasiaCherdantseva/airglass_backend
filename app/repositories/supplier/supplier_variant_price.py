from app.models.suppliers.supplier_variant_price import SupplierVariantPrice
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.suppliers.supplier_variant_price import (
    SupplierVariantPriceReadRepositoryProtocol,
    SupplierVariantPriceWriteRepositoryProtocol,
)


class SupplierVariantPriceRepository(
    BaseIdRepository[SupplierVariantPrice],
    SupplierVariantPriceReadRepositoryProtocol,
    SupplierVariantPriceWriteRepositoryProtocol,
):
    """Repository for supplier variant price history.

    Репозиторий истории цен предложений поставщиков.
    """

    model = SupplierVariantPrice
