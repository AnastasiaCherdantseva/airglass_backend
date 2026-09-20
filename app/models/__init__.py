"""
Главный __init__.py для всех моделей.
Экспортирует ВСЕ модели, чтобы Alembic и SQLAlchemy видели их.
"""

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
# BASE
# ============================================
from app.models.base import Base

# ============================================
# CATALOG
# ============================================
from app.models.catalog import (
    Category,
    CategoryColorGroup,
    CategoryMaterialGroup,
    Color,
    ColorGroup,
    ColorVisualType,
    Material,
    MaterialGroup,
    Product,
    ProductStatus,
    ProductVariant,
    ProductVariantStatus,
    Unit,
    VisualType,
)

# ============================================
# CUSTOMERS
# ============================================
from app.models.customers import (
    AddressType,
    Customer,
    CustomerAddress,
)

# ============================================
# DOCUMENTS
# ============================================
from app.models.documents import (
    DocumentType,
    GeneratedDocument,
)

# ============================================
# MEDIA
# ============================================
from app.models.media import (
    CategoryMediaRule,
    MediaFile,
    MediaType,
    ProductMedia,
    ProductMediaType,
    UserMedia,
)
from app.models.mixins import SoftDeleteMixin, TimestampMixin

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
    QuoteItem,
    QuoteItemGroup,
    QuoteItemGroupType,
    QuoteItemSourceType,
    QuoteStatus,
    QuoteVersion,
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
# SYSTEM (Users, Roles, Permissions)
# ============================================
from app.models.system import (
    AuditLog,
    Organization,
    Permission,
    PermissionAction,
    PermissionCondition,
    PermissionConditionType,
    PermissionResource,
    PermissionScope,
    Role,
    RolePermission,
    Session,
    User,
    UserOrganization,
    UserPermission,
    UserRole,
)

# ============================================
# TEMPLATES
# ============================================
from app.models.templates import (
    BindingType,
    GalleryRule,
    GalleryRuleCondition,
    Template,
    TemplateGallery,
    TemplateItem,
    TemplateMediaRule,
    TemplateType,
)

# ============================================
# USAGE
# ============================================
from app.models.usage import (
    CategoryUsageRole,
    ProductUsageRole,
    UsageRole,
    VariantUsageRole,
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
    "ColorVisualType",
    "VisualType",
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
    "Session",
    "Organization",
    "UserOrganization",
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
