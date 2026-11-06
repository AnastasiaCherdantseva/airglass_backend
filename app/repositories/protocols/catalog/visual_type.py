from typing import Protocol

from app.models.catalog.visual_type import VisualType
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class VisualTypeReadRepositoryProtocol(
    ReadRepositoryProtocol[VisualType],
    Protocol,
):
    pass


class VisualTypeWriteRepositoryProtocol(
    WriteRepositoryProtocol[VisualType],
    Protocol,
):
    pass


class VisualTypeRepositoryProtocol(
    VisualTypeReadRepositoryProtocol,
    VisualTypeWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for visual types.

    Контракт репозитория типов визуализации.
    """
