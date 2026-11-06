from app.repositories.protocols.catalog.category import (
    CategoryReadRepositoryProtocol,
    CategoryRepositoryProtocol,
    CategoryWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.category_attributes import (
    CategoryAttributeReadRepositoryProtocol,
    CategoryAttributeRepositoryProtocol,
    CategoryAttributeWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.category_color_group import (
    CategoryColorGroupReadRepositoryProtocol,
    CategoryColorGroupRepositoryProtocol,
    CategoryColorGroupWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.category_material_group import (
    CategoryMaterialGroupReadRepositoryProtocol,
    CategoryMaterialGroupRepositoryProtocol,
    CategoryMaterialGroupWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.color import (
    ColorReadRepositoryProtocol,
    ColorRepositoryProtocol,
    ColorWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.color_group import (
    ColorGroupReadRepositoryProtocol,
    ColorGroupRepositoryProtocol,
    ColorGroupWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.color_visual_type import (
    ColorVisualTypeReadRepositoryProtocol,
    ColorVisualTypeRepositoryProtocol,
    ColorVisualTypeWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.material import (
    MaterialReadRepositoryProtocol,
    MaterialRepositoryProtocol,
    MaterialWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.material_group import (
    MaterialGroupReadRepositoryProtocol,
    MaterialGroupRepositoryProtocol,
    MaterialGroupWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.product import (
    ProductReadRepositoryProtocol,
    ProductRepositoryProtocol,
    ProductWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.product_variant import (
    ProductVariantReadRepositoryProtocol,
    ProductVariantRepositoryProtocol,
    ProductVariantWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.unit import (
    UnitReadRepositoryProtocol,
    UnitRepositoryProtocol,
    UnitWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.variant_attribute import (
    VariantAttributeValueReadRepositoryProtocol,
    VariantAttributeValueRepositoryProtocol,
    VariantAttributeValueWriteRepositoryProtocol,
)
from app.repositories.protocols.catalog.visual_type import (
    VisualTypeReadRepositoryProtocol,
    VisualTypeRepositoryProtocol,
    VisualTypeWriteRepositoryProtocol,
)

__all__ = [
    "CategoryReadRepositoryProtocol",
    "CategoryWriteRepositoryProtocol",
    "CategoryRepositoryProtocol",
    "CategoryAttributeRepositoryProtocol",
    "CategoryAttributeWriteRepositoryProtocol",
    "CategoryAttributeReadRepositoryProtocol",
    "CategoryColorGroupRepositoryProtocol",
    "CategoryColorGroupReadRepositoryProtocol",
    "CategoryColorGroupWriteRepositoryProtocol",
    "CategoryMaterialGroupRepositoryProtocol",
    "CategoryMaterialGroupReadRepositoryProtocol",
    "CategoryMaterialGroupWriteRepositoryProtocol",
    "ColorRepositoryProtocol",
    "ColorWriteRepositoryProtocol",
    "ColorReadRepositoryProtocol",
    "ColorGroupRepositoryProtocol",
    "ColorGroupWriteRepositoryProtocol",
    "ColorGroupReadRepositoryProtocol",
    "ColorVisualTypeRepositoryProtocol",
    "ColorVisualTypeWriteRepositoryProtocol",
    "ColorVisualTypeReadRepositoryProtocol",
    "MaterialRepositoryProtocol",
    "MaterialWriteRepositoryProtocol",
    "MaterialReadRepositoryProtocol",
    "MaterialGroupRepositoryProtocol",
    "MaterialGroupWriteRepositoryProtocol",
    "MaterialGroupReadRepositoryProtocol",
    "ProductRepositoryProtocol",
    "ProductWriteRepositoryProtocol",
    "ProductReadRepositoryProtocol",
    "ProductVariantRepositoryProtocol",
    "ProductVariantWriteRepositoryProtocol",
    "ProductVariantReadRepositoryProtocol",
    "UnitRepositoryProtocol",
    "UnitWriteRepositoryProtocol",
    "UnitReadRepositoryProtocol",
    "VariantAttributeValueRepositoryProtocol",
    "VariantAttributeValueWriteRepositoryProtocol",
    "VariantAttributeValueReadRepositoryProtocol",
    "VisualTypeRepositoryProtocol",
    "VisualTypeWriteRepositoryProtocol",
    "VisualTypeReadRepositoryProtocol",
]
