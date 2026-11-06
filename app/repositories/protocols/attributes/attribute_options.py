from typing import Protocol

from app.models.attributes.attribute_option import AttributeOption
from app.repositories.protocols.base import ReadRepositoryProtocol, WriteRepositoryProtocol


class AttributeOptionReadRepositoryProtocol(
    ReadRepositoryProtocol[AttributeOption],
    Protocol,
):
    pass


class AttributeOptionWriteRepositoryProtocol(
    WriteRepositoryProtocol[AttributeOption],
    Protocol,
):
    pass


class AttributeOptionRepositoryProtocol(
    AttributeOptionWriteRepositoryProtocol,
    AttributeOptionReadRepositoryProtocol,
    Protocol,
):
    """Repository contract for attribute options.

    Контракт репозитория вариантов значений атрибутов.
    """
