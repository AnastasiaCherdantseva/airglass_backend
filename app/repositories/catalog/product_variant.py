from app.models.catalog.product_variant import ProductVariant
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.product_variant import (
    ProductVariantReadRepositoryProtocol,
    ProductVariantWriteRepositoryProtocol,
)


class ProductVariantRepository(
    BaseIdRepository[ProductVariant],
    ProductVariantReadRepositoryProtocol,
    ProductVariantWriteRepositoryProtocol,
):
    """Repository for product variants.

    Репозиторий вариаций товаров.
    """

    model = ProductVariant
