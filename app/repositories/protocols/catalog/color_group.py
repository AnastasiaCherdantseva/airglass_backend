from typing import Protocol

from app.models.catalog.color_group import ColorGroup
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class ColorGroupRepositoryProtocol(
    ReadRepositoryProtocol[ColorGroup],
    WriteRepositoryProtocol[ColorGroup],
    Protocol,
):
    """Repository contract for color groups.

    Контракт репозитория групп цветов.
    """
