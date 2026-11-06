from typing import Protocol

from app.models.attributes.attribute_option import AttributeOption
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class AttributeOptionRepositoryProtocol(
    ReadRepositoryProtocol[AttributeOption],
    WriteRepositoryProtocol[AttributeOption],
    Protocol,
):
    """Repository contract for attribute options.

    Контракт репозитория вариантов значений атрибутов.
    """
