from app.models.attributes.attribute_option import AttributeOption
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.attributes.attribute_options import (
    AttributeOptionReadRepositoryProtocol,
    AttributeOptionWriteRepositoryProtocol,
)


class AttributeOptionRepository(
    BaseIdRepository[AttributeOption],
    AttributeOptionReadRepositoryProtocol,
    AttributeOptionWriteRepositoryProtocol,
):
    """Repository for attribute options.

    Репозиторий вариантов значений атрибутов.
    """

    model = AttributeOption
