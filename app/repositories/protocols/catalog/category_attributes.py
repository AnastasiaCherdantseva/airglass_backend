from typing import Protocol


class CategoryAttributeWriteRepositoryProtocol(
    Protocol,
):
    pass


class CategoryAttributeReadRepositoryProtocol(
    Protocol,
):
    pass


class CategoryAttributeRepositoryProtocol(
    CategoryAttributeWriteRepositoryProtocol,
    CategoryAttributeReadRepositoryProtocol,
    Protocol,
):
    """Repository contract for category-attribute links.

    Контракт репозитория связей категорий и атрибутов.
    """
