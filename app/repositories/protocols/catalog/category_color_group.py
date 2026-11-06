from typing import Protocol


class CategoryColorGroupReadRepositoryProtocol(
    Protocol,
):
    pass


class CategoryColorGroupWriteRepositoryProtocol(
    Protocol,
):
    pass


class CategoryColorGroupRepositoryProtocol(
    CategoryColorGroupReadRepositoryProtocol,
    CategoryColorGroupWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for category-color-group links.

    Контракт репозитория связей категорий и групп цветов.
    """

    pass
