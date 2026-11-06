from typing import Protocol


class VariantAttributeValueReadRepositoryProtocol(
    Protocol,
):
    pass


class VariantAttributeValueWriteRepositoryProtocol(
    Protocol,
):
    pass


class VariantAttributeValueRepositoryProtocol(
    VariantAttributeValueReadRepositoryProtocol,
    VariantAttributeValueWriteRepositoryProtocol,
    Protocol,
):
    """Repository contract for variant attribute values.

    Контракт репозитория значений атрибутов вариаций.
    """
