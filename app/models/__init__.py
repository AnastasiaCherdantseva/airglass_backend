"""
Главный __init__.py для всех моделей.
Экспортирует ВСЕ модели, чтобы Alembic и SQLAlchemy видели их.
"""

# ============================================
# BASE
# ============================================
from app.models.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin

# ============================================
# CATALOG
# ============================================
from app.models.catalog import (
    Category,
    Product,
    ProductStatus,
    ProductVariant,
    ProductVariantStatus,
    Color,
    Material,
    Unit,
    ColorGroup,
    CategoryColorGroup,
    MaterialGroup,
    CategoryMaterialGroup

)

# ============================================
# ATTRIBUTES
# ============================================
from app.models.attributes import (
    Attribute,
    AttributeDataType,
    AttributeOption,
    CategoryAttribute,
    VariantAttributeValue,
)

# ============================================
# SUPPLIERS
# ============================================
from app.models.suppliers import (
    Supplier,
    SupplierVariant,
    SupplierVariantPrice,
)

# ============================================
# USAGE
# ============================================
from app.models.usage import (
    UsageRole,
    ProductUsageRole,
    VariantUsageRole,
    CategoryUsageRole,
)

# ============================================
# MEDIA
# ============================================
from app.models.media import (
    MediaFile,
    MediaType,
    ProductMedia,
    ProductMediaType,
    CategoryMediaRule,
    UserMedia
)

# ============================================
# TEMPLATES
# ============================================
from app.models.templates import (
    Template,
    TemplateType,
    TemplateItem,
    TemplateMediaRule,
    GalleryRule,
    GalleryRuleCondition,
    TemplateGallery,
    BindingType
)

# ============================================
# SYSTEM (Users, Roles, Permissions)
# ============================================
from app.models.system import (
    User,
    Role,
    Permission,
    PermissionResource,
    PermissionAction,
    PermissionScope,
    PermissionCondition,
    PermissionConditionType,
    RolePermission,
    UserRole,
    UserPermission,
    AuditLog,
)

# ============================================
# CUSTOMERS
# ============================================
from app.models.customers import (
    Customer,
    CustomerAddress,
    AddressType,
)

# ============================================
# PROJECTS
# ============================================
from app.models.projects import (
    Project,
    ProjectStatus,
)

# ============================================
# QUOTES
# ============================================
from app.models.quotes import (
    Quote,
    QuoteStatus,
    QuoteVersion,
    QuoteItemGroup,
    QuoteItemGroupType,
    QuoteItem,
    QuoteItemSourceType,
)

# ============================================
# DOCUMENTS
# ============================================
from app.models.documents import (
    GeneratedDocument,
    DocumentType,
)


# ============================================
# ЭКСПОРТ ВСЕХ МОДЕЛЕЙ
# ============================================
__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",

    # Catalog
    "Category",
    "Product",
    "ProductStatus",
    "ProductVariant",
    "ProductVariantStatus",
    "Color",
    "Material",
    "Unit",
    "ColorGroup",
    "CategoryColorGroup",
    "MaterialGroup",
    "CategoryMaterialGroup",

    # Attributes
    "Attribute",
    "AttributeDataType",
    "AttributeOption",
    "CategoryAttribute",
    "VariantAttributeValue",

    # Suppliers
    "Supplier",
    "SupplierVariant",
    "SupplierVariantPrice",

    # Usage
    "UsageRole",
    "ProductUsageRole",
    "VariantUsageRole",
    "CategoryUsageRole",

    # Media
    "MediaFile",
    "MediaType",
    "ProductMedia",
    "ProductMediaType",
    "CategoryMediaRule",
    "UserMedia",

    # Templates
    "Template",
    "TemplateType",
    "TemplateItem",
    "TemplateMediaRule",
    "GalleryRule",
    "GalleryRuleCondition",
    "TemplateGallery",
    "BindingType",

    # System
    "User",
    "Role",
    "Permission",
    "PermissionResource",
    "PermissionAction",
    "PermissionScope",
    "PermissionCondition",
    "PermissionConditionType",
    "RolePermission",
    "UserRole",
    "UserPermission",
    "AuditLog",

    # Customers
    "Customer",
    "CustomerAddress",
    "AddressType",

    # Projects
    "Project",
    "ProjectStatus",

    # Quotes
    "Quote",
    "QuoteStatus",
    "QuoteVersion",
    "QuoteItemGroup",
    "QuoteItemGroupType",
    "QuoteItem",
    "QuoteItemSourceType",

    # Documents
    "GeneratedDocument",
    "DocumentType",
]