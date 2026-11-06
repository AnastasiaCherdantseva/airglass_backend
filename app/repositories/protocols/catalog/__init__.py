from app.repositories.protocols.catalog.category import (
    CategoryReadRepositoryProtocol,
    CategoryRepositoryProtocol,
    CategoryWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.category_attributes import (
    CategoryAttributeRepositoryProtocol,
)
from app.repositories.protocols.catalog.category_color_group import (
    CategoryColorGroupRepositoryProtocol,
)
from app.repositories.protocols.catalog.category_material_group import (
    CategoryMaterialGroupRepositoryProtocol,
)
from app.repositories.protocols.catalog.color import (
    ColorRepositoryProtocol,
)
from app.repositories.protocols.catalog.color_group import (
    ColorGroupRepositoryProtocol,
)
from app.repositories.protocols.catalog.color_visual_type import (
    ColorVisualTypeRepositoryProtocol,
)
from app.repositories.protocols.catalog.material import (
    MaterialRepositoryProtocol,
)
from app.repositories.protocols.catalog.material_group import (
    MaterialGroupRepositoryProtocol,
)
from app.repositories.protocols.catalog.product import (
    ProductRepositoryProtocol,
)
from app.repositories.protocols.catalog.product_variant import (
    ProductVariantRepositoryProtocol,
)
from app.repositories.protocols.catalog.unit import (
    UnitRepositoryProtocol,
)
from app.repositories.protocols.catalog.variant_attribute import (
    VariantAttributeValueRepositoryProtocol,
)
from app.repositories.protocols.catalog.visual_type import (
    VisualTypeRepositoryProtocol,
)

__all__ = [
    "CategoryReadRepositoryProtocol",
    "CategoryWriteRepositoryProtocol",
    "CategoryRepositoryProtocol",
    "CategoryAttributeRepositoryProtocol",
    "CategoryColorGroupRepositoryProtocol",
    "CategoryMaterialGroupRepositoryProtocol",
    "ColorRepositoryProtocol",
    "ColorGroupRepositoryProtocol",
    "ColorVisualTypeRepositoryProtocol",
    "MaterialRepositoryProtocol",
    "MaterialGroupRepositoryProtocol",
    "ProductRepositoryProtocol",
    "ProductVariantRepositoryProtocol",
    "UnitRepositoryProtocol",
    "VariantAttributeValueRepositoryProtocol",
    "VisualTypeRepositoryProtocol",
]
