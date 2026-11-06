from app.repositories.protocols.suppliers.supplier import (
    SupplierReadRepositoryProtocol,
    SupplierRepositoryProtocol,
    SupplierWriteRepositoryProtocol,
)
from app.repositories.protocols.suppliers.supplier_variant import (
    SupplierVariantReadRepositoryProtocol,
    SupplierVariantRepositoryProtocol,
    SupplierVariantWriteRepositoryProtocol,
)
from app.repositories.protocols.suppliers.supplier_variant_price import (
    SupplierVariantPriceReadRepositoryProtocol,
    SupplierVariantPriceRepositoryProtocol,
    SupplierVariantPriceWriteRepositoryProtocol,
)

__all__ = [
    "SupplierRepositoryProtocol",
    "SupplierWriteRepositoryProtocol",
    "SupplierReadRepositoryProtocol",
    "SupplierVariantRepositoryProtocol",
    "SupplierVariantWriteRepositoryProtocol",
    "SupplierVariantReadRepositoryProtocol",
    "SupplierVariantPriceRepositoryProtocol",
    "SupplierVariantPriceWriteRepositoryProtocol",
    "SupplierVariantPriceReadRepositoryProtocol",
]
