from typing import Protocol

from app.models.catalog.visual_type import VisualType
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class VisualTypeRepositoryProtocol(
    ReadRepositoryProtocol[VisualType],
    WriteRepositoryProtocol[VisualType],
    Protocol,
):
    """Repository contract for visual types.

    Контракт репозитория типов визуализации.
    """
