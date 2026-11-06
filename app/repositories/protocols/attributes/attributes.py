from typing import Protocol

from app.models.attributes.attribute import Attribute
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class AttributeReadRepositoryProtocol(
    ReadRepositoryProtocol[Attribute],
    Protocol,
):
    pass


class AttributeWriteRepositoryProtocol(
    WriteRepositoryProtocol[Attribute],
    Protocol,
):
    pass


class AttributeRepositoryProtocol(
    AttributeReadRepositoryProtocol,
    AttributeWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for attributes.

    Контракт репозитория атрибутов.
    """
