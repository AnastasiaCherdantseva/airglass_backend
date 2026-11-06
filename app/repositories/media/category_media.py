from app.models.media.category_media_rule import CategoryMediaRule
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.media.category_media_rule import (
    CategoryMediaRuleReadRepositoryProtocol,
    CategoryMediaRuleWriteRepositoryProtocol,
)


class CategoryMediaRuleRepository(
    BaseIdRepository[CategoryMediaRule],
    CategoryMediaRuleReadRepositoryProtocol,
    CategoryMediaRuleWriteRepositoryProtocol,
):
    """Repository for category media rules.

    Репозиторий правил медиа категорий.
    """

    model = CategoryMediaRule
