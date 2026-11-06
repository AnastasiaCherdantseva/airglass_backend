from app.models.catalog.color import Color
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.color import (
    ColorReadRepositoryProtocol,
    ColorWriteRepositoryProtocol,
)


class ColorRepository(
    BaseIdRepository[Color], ColorReadRepositoryProtocol, ColorWriteRepositoryProtocol
):
    """Repository for colors.

    Репозиторий цветов.
    """

    model = Color
