from typing import Protocol

from app.models.catalog.unit import Unit
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class UnitRepositoryProtocol(
    ReadRepositoryProtocol[Unit],
    WriteRepositoryProtocol[Unit],
    Protocol,
):
    """Repository contract for measurement units.

    Контракт репозитория единиц измерения.
    """
