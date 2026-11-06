from typing import Protocol


class CategoryMaterialGroupReadRepositoryProtocol(
    Protocol,
):
    pass


class CategoryMaterialGroupWriteRepositoryProtocol(
    Protocol,
):
    pass


class CategoryMaterialGroupRepositoryProtocol(
    CategoryMaterialGroupReadRepositoryProtocol,
    CategoryMaterialGroupWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for category-material-group links.

    Контракт репозитория связей категорий и групп материалов.
    """

    pass
