"""
FastAPI-зависимости.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends

from app.core.database import AsyncSessionLocal
from app.core.uow import UnitOfWork
from app.repositories.attribute import (
    AttributeOptionRepository,
    AttributeRepository,
)
from app.repositories.catalog import (
    CategoryAttributeRepository,
    CategoryColorGroupRepository,
    CategoryMaterialGroupRepository,
    CategoryRepository,
    ColorGroupRepository,
    ColorRepository,
    ColorVisualTypeRepository,
    MaterialGroupRepository,
    MaterialRepository,
    ProductRepository,
    ProductVariantRepository,
    UnitRepository,
    VariantAttributeValueRepository,
    VisualTypeRepository,
)
from app.repositories.media import (
    MediaFileRepository,
    MediaTypeRepository,
    ProductMediaRepository,
)
from app.repositories.supplier import (
    SupplierRepository,
    SupplierVariantPriceRepository,
    SupplierVariantRepository,
)
from app.repositories.system import (
    OrganizationRepository,
    PermissionConditionRepository,
    PermissionRepository,
    RolePermissionRepository,
    RoleRepository,
    SessionRepository,
    UserDirectPermissionRepository,
    UserOrganizationRepository,
    UserPermissionRepository,
    UserRepository,
    UserRoleRepository,
)
from app.repositories.usage import (
    CategoryUsageRoleRepository,
    ProductUsageRoleRepository,
    UsageRoleRepository,
    VariantUsageRoleRepository,
)


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    async with AsyncSessionLocal() as session:
        async with UnitOfWork(session) as uow:
            yield uow


def get_session_repo(uow: UnitOfWork = Depends(get_uow)) -> SessionRepository:
    return SessionRepository(uow.session)


def get_user_repo(uow: UnitOfWork = Depends(get_uow)) -> UserRepository:
    return UserRepository(uow.session)


def get_role_repo(uow: UnitOfWork = Depends(get_uow)) -> RoleRepository:
    return RoleRepository(uow.session)


def get_organization_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> OrganizationRepository:
    return OrganizationRepository(uow.session)


def get_permission_repo(uow: UnitOfWork = Depends(get_uow)) -> PermissionRepository:
    return PermissionRepository(uow.session)


def get_permission_condition_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> PermissionConditionRepository:
    return PermissionConditionRepository(uow.session)


def get_user_role_repo(uow: UnitOfWork = Depends(get_uow)) -> UserRoleRepository:
    return UserRoleRepository(uow.session)


def get_role_permission_repo(uow: UnitOfWork = Depends(get_uow)) -> RolePermissionRepository:
    return RolePermissionRepository(uow.session)


def get_user_direct_permission_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> UserDirectPermissionRepository:
    return UserDirectPermissionRepository(uow.session)


def get_user_permission_repo(uow: UnitOfWork = Depends(get_uow)) -> UserPermissionRepository:
    return UserPermissionRepository(uow.session)


def get_user_organization_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> UserOrganizationRepository:
    return UserOrganizationRepository(uow.session)


def get_category_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> CategoryRepository:
    """Get category repository.

    Получить репозиторий категорий.
    """
    return CategoryRepository(uow.session)


def get_product_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> ProductRepository:
    """Get product repository.

    Получить репозиторий товаров.
    """
    return ProductRepository(uow.session)


def get_product_variant_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> ProductVariantRepository:
    """Get product variant repository.

    Получить репозиторий вариаций товаров.
    """
    return ProductVariantRepository(uow.session)


def get_unit_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> UnitRepository:
    """Get measurement unit repository.

    Получить репозиторий единиц измерения.
    """
    return UnitRepository(uow.session)


def get_color_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> ColorRepository:
    """Get color repository.

    Получить репозиторий цветов.
    """
    return ColorRepository(uow.session)


def get_material_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> MaterialRepository:
    """Get material repository.

    Получить репозиторий материалов.
    """
    return MaterialRepository(uow.session)


def get_color_group_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> ColorGroupRepository:
    """Get color group repository.

    Получить репозиторий групп цветов.
    """
    return ColorGroupRepository(uow.session)


def get_material_group_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> MaterialGroupRepository:
    """Get material group repository.

    Получить репозиторий групп материалов.
    """
    return MaterialGroupRepository(uow.session)


def get_visual_type_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> VisualTypeRepository:
    """Get visual type repository.

    Получить репозиторий типов визуализации.
    """
    return VisualTypeRepository(uow.session)


# Attributes


def get_attribute_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> AttributeRepository:
    """Get attribute repository.

    Получить репозиторий атрибутов.
    """
    return AttributeRepository(uow.session)


def get_attribute_option_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> AttributeOptionRepository:
    """Get attribute option repository.

    Получить репозиторий вариантов значений атрибутов.
    """
    return AttributeOptionRepository(uow.session)


def get_variant_attribute_value_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> VariantAttributeValueRepository:
    """Get variant attribute value repository.

    Получить репозиторий значений атрибутов вариаций.
    """
    return VariantAttributeValueRepository(uow.session)


def get_category_attribute_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> CategoryAttributeRepository:
    """Get category attribute relation repository.

    Получить репозиторий связей категорий и атрибутов.
    """
    return CategoryAttributeRepository(uow.session)


# Suppliers


def get_supplier_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> SupplierRepository:
    """Get supplier repository.

    Получить репозиторий поставщиков.
    """
    return SupplierRepository(uow.session)


def get_supplier_variant_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> SupplierVariantRepository:
    """Get supplier variant repository.

    Получить репозиторий предложений поставщиков.
    """
    return SupplierVariantRepository(uow.session)


def get_supplier_variant_price_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> SupplierVariantPriceRepository:
    """Get supplier variant price repository.

    Получить репозиторий истории цен предложений поставщиков.
    """
    return SupplierVariantPriceRepository(uow.session)


# Media


def get_media_file_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> MediaFileRepository:
    """Get media file repository.

    Получить репозиторий медиафайлов.
    """
    return MediaFileRepository(uow.session)


def get_media_type_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> MediaTypeRepository:
    """Get media type repository.

    Получить репозиторий типов медиа.
    """
    return MediaTypeRepository(uow.session)


def get_product_media_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> ProductMediaRepository:
    """Get product media repository.

    Получить репозиторий медиа товаров.
    """
    return ProductMediaRepository(uow.session)


# Usage roles


def get_usage_role_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> UsageRoleRepository:
    """Get usage role repository.

    Получить репозиторий ролей использования.
    """
    return UsageRoleRepository(uow.session)


def get_product_usage_role_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> ProductUsageRoleRepository:
    """Get product usage role relation repository.

    Получить репозиторий связей товаров и ролей использования.
    """
    return ProductUsageRoleRepository(uow.session)


def get_variant_usage_role_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> VariantUsageRoleRepository:
    """Get variant usage role relation repository.

    Получить репозиторий связей вариаций и ролей использования.
    """
    return VariantUsageRoleRepository(uow.session)


def get_category_usage_role_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> CategoryUsageRoleRepository:
    """Get category usage role relation repository.

    Получить репозиторий связей категорий и ролей использования.
    """
    return CategoryUsageRoleRepository(uow.session)


# Category configuration


def get_category_color_group_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> CategoryColorGroupRepository:
    """Get category color group repository.

    Получить репозиторий связей категорий и групп цветов.
    """
    return CategoryColorGroupRepository(uow.session)


def get_category_material_group_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> CategoryMaterialGroupRepository:
    """Get category material group repository.

    Получить репозиторий связей категорий и групп материалов.
    """
    return CategoryMaterialGroupRepository(uow.session)


def get_color_visual_type_repo(
    uow: UnitOfWork = Depends(get_uow),
) -> ColorVisualTypeRepository:
    """Get color visual type repository.

    Получить репозиторий связей цветов и типов визуализации.
    """
    return ColorVisualTypeRepository(uow.session)
