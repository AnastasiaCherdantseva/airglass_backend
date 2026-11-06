from app.repositories.protocols.suppliers.supplier import (
    SupplierRepositoryProtocol,
)
from app.repositories.protocols.suppliers.supplier_variant import (
    SupplierVariantRepositoryProtocol,
)
from app.repositories.protocols.suppliers.supplier_variant_price import (
    SupplierVariantPriceRepositoryProtocol,
)

__all__ = [
    "SupplierRepositoryProtocol",
    "SupplierVariantRepositoryProtocol",
    "SupplierVariantPriceRepositoryProtocol",
]
