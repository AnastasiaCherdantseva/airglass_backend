import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.catalog.category import Category
    from app.models.media.product_media import ProductMedia
    from app.models.usage.product_usage_role import ProductUsageRole
    from app.models.catalog.product_variant import ProductVariant
    from app.models.catalog.unit import Unit


class ProductStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DISCONTINUED = "DISCONTINUED"


class Product(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
    )
    unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("units.id", ondelete="RESTRICT"),
    )
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
    )
    status: Mapped[ProductStatus] = mapped_column(   # ← ProductStatus, не ProductVariantStatus
        Enum(ProductStatus),
        default=ProductStatus.ACTIVE,
        server_default=text("'ACTIVE'"),
    )

    # Связи
    category: Mapped["Category"] = relationship(back_populates="products")
    unit: Mapped["Unit"] = relationship(back_populates="products")
    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    product_media: Mapped[list["ProductMedia"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    product_usage_roles: Mapped[list["ProductUsageRole"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )