from typing import Protocol

from app.models.attributes.attribute import Attribute
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class AttributeRepositoryProtocol(
    ReadRepositoryProtocol[Attribute],
    WriteRepositoryProtocol[Attribute],
    Protocol,
):
    """Repository contract for attributes.

    Контракт репозитория атрибутов.
    """
