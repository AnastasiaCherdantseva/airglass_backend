from typing import Protocol


class ProductMediaReadRepositoryProtocol(
    Protocol,
):
    pass


class ProductMediaWriteRepositoryProtocol(
    Protocol,
):
    pass


class ProductMediaRepositoryProtocol(
    ProductMediaReadRepositoryProtocol,
    ProductMediaWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for product media.

    Контракт репозитория медиа товаров.
    """
