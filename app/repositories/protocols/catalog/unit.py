from typing import Protocol

from app.models.catalog.unit import Unit
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class UnitReadRepositoryProtocol(
    ReadRepositoryProtocol[Unit],
    Protocol,
):
    pass


class UnitWriteRepositoryProtocol(
    WriteRepositoryProtocol[Unit],
    Protocol,
):
    pass


class UnitRepositoryProtocol(
    UnitReadRepositoryProtocol,
    UnitWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for measurement units.

    Контракт репозитория единиц измерения.
    """
