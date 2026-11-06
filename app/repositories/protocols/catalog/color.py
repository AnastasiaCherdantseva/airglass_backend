from typing import Protocol

from app.models.catalog.color import Color
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class ColorRepositoryProtocol(
    ReadRepositoryProtocol[Color],
    WriteRepositoryProtocol[Color],
    Protocol,
):
    """Repository contract for colors.

    Контракт репозитория цветов.
    """
