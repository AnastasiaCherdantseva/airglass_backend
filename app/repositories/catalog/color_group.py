from app.models.catalog.color_group import ColorGroup
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.color_group import (
    ColorGroupReadRepositoryProtocol,
    ColorGroupWriteRepositoryProtocol,
)


class ColorGroupRepository(
    BaseIdRepository[ColorGroup],
    ColorGroupReadRepositoryProtocol,
    ColorGroupWriteRepositoryProtocol,
):
    """Repository for color groups.

    Репозиторий групп цветов.
    """

    model = ColorGroup
