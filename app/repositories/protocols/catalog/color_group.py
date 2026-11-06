from typing import Protocol

from app.models.catalog.color_group import ColorGroup
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class ColorGroupReadRepositoryProtocol(
    ReadRepositoryProtocol[ColorGroup],
    Protocol,
):
    pass
    """Repository contract for color groups.

    Контракт репозитория групп цветов.
    """


class ColorGroupWriteRepositoryProtocol(
    WriteRepositoryProtocol[ColorGroup],
    Protocol,
):
    pass
    """Repository contract for color groups.

    Контракт репозитория групп цветов.
    """


class ColorGroupRepositoryProtocol(
    ColorGroupReadRepositoryProtocol,
    ColorGroupWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for color groups.

    Контракт репозитория групп цветов.
    """

    pass
