from typing import Protocol

from app.models.catalog.color import Color
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class ColorReadRepositoryProtocol(
    ReadRepositoryProtocol[Color],
    Protocol,
):
    pass


class ColorWriteRepositoryProtocol(
    WriteRepositoryProtocol[Color],
    Protocol,
):
    pass


class ColorRepositoryProtocol(
    ColorReadRepositoryProtocol,
    ColorWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for colors.

    Контракт репозитория цветов.
    """

    pass
