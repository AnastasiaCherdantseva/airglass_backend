from app.repositories.catalog.category import CategoryRepository
from app.repositories.catalog.category_attribute import CategoryAttributeRepository
from app.repositories.catalog.category_color_group import CategoryColorGroupRepository
from app.repositories.catalog.category_material_group import CategoryMaterialGroupRepository
from app.repositories.catalog.color import ColorRepository
from app.repositories.catalog.color_group import ColorGroupRepository
from app.repositories.catalog.color_visual_type import ColorVisualTypeRepository
from app.repositories.catalog.material import MaterialRepository
from app.repositories.catalog.material_group import MaterialGroupRepository
from app.repositories.catalog.product import ProductRepository
from app.repositories.catalog.product_variant import ProductVariantRepository
from app.repositories.catalog.unit import UnitRepository
from app.repositories.catalog.variant_attribute import VariantAttributeValueRepository
from app.repositories.catalog.visual_type import VisualTypeRepository

__all__ = [
    "ColorGroupRepository",
    "ColorRepository",
    "CategoryRepository",
    "VisualTypeRepository",
    "VariantAttributeValueRepository",
    "MaterialGroupRepository",
    "MaterialRepository",
    "UnitRepository",
    "ProductVariantRepository",
    "ProductRepository",
    "CategoryAttributeRepository",
    "CategoryColorGroupRepository",
    "CategoryMaterialGroupRepository",
    "ColorVisualTypeRepository",
]
