from app.models.attributes.variant_attribute_value import VariantAttributeValue
from app.repositories.base import BaseIdRepository
from app.repositories.protocols.catalog.variant_attribute import (
    VariantAttributeValueReadRepositoryProtocol,
    VariantAttributeValueWriteRepositoryProtocol,
)


class VariantAttributeValueRepository(
    BaseIdRepository[VariantAttributeValue],
    VariantAttributeValueReadRepositoryProtocol,
    VariantAttributeValueWriteRepositoryProtocol,
):
    """Repository for variant attribute values.

    Репозиторий значений атрибутов вариаций.
    """

    model = VariantAttributeValue
