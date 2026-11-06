from typing import Protocol


class CategoryMediaRuleReadRepositoryProtocol(
    Protocol,
):
    pass


class CategoryMediaRuleWriteRepositoryProtocol(
    Protocol,
):
    pass


class CategoryMediaRuleRepositoryProtocol(
    CategoryMediaRuleReadRepositoryProtocol,
    CategoryMediaRuleWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for category media rules.

    Контракт репозитория правил медиа категорий.
    """
