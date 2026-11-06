from app.models.catalog.product import Product
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.product import (
    ProductReadRepositoryProtocol,
    ProductWriteRepositoryProtocol,
)


class ProductRepository(
    BaseIdRepository[Product], ProductReadRepositoryProtocol, ProductWriteRepositoryProtocol
):
    """Repository for products.

    Репозиторий товаров.
    """

    model = Product
