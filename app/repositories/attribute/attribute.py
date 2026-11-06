from app.models.attributes.attribute import Attribute
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.attributes.attributes import (
    AttributeReadRepositoryProtocol,
    AttributeWriteRepositoryProtocol,
)


class AttributeRepository(
    BaseIdRepository[Attribute], AttributeReadRepositoryProtocol, AttributeWriteRepositoryProtocol
):
    """Repository for attributes.

    Репозиторий атрибутов.
    """

    model = Attribute
