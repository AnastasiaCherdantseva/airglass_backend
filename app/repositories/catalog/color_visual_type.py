from app.models.catalog.color_visual_type import ColorVisualType
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.color_visual_type import (
    ColorVisualTypeReadRepositoryProtocol,
    ColorVisualTypeWriteRepositoryProtocol,
)


class ColorVisualTypeRepository(
    BaseIdRepository[ColorVisualType],
    ColorVisualTypeReadRepositoryProtocol,
    ColorVisualTypeWriteRepositoryProtocol,
):
    """Repository for color-visual-type links.

    Репозиторий связей цветов и типов визуализации.
    """

    model = ColorVisualType
