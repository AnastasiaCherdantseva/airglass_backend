from app.models.media.product_media import ProductMedia
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.media.product_media import (
    ProductMediaReadRepositoryProtocol,
    ProductMediaWriteRepositoryProtocol,
)


class ProductMediaRepository(
    BaseIdRepository[ProductMedia],
    ProductMediaReadRepositoryProtocol,
    ProductMediaWriteRepositoryProtocol,
):
    """Repository for product media.

    Репозиторий медиа товаров.
    """

    model = ProductMedia
