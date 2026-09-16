import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean, ForeignKey, UniqueConstraint, Enum, Index, text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin


class ProductVariantStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"              # активен, доступен для новых КП/шаблонов
    ARCHIVED = "ARCHIVED"          # скрыт администратором (не удалён!)
    DISCONTINUED = "DISCONTINUED"  # снят с производства


class ProductVariant(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "color_id",
            "material_id",
            name="uq_variant_product_color_material",
        ),
        Index("ix_variant_product_id", "product_id"),
        Index("ix_variant_color_id", "color_id"),
        Index("ix_variant_material_id", "material_id"),
        Index("ix_variant_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            server_default=text("gen_random_uuid()"),
        )
    product_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )
    color_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("colors.id", ondelete="RESTRICT"),
        nullable=True,
    )
    material_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("materials.id", ondelete="RESTRICT"),
        nullable=True,
    )
    internal_sku : Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    name_override : Mapped[str] = mapped_column(String(255), nullable=True)
    is_active = Column(
    Boolean,
    default=True,
    nullable=False,
    server_default=text("true"),
)
    status : Mapped[ProductVariantStatus] = mapped_column(
        Enum(ProductVariantStatus),
        default=ProductVariantStatus.ACTIVE,
        nullable=False,
        server_default=text("'ACTIVE'")
    )

    # Связи
    product = relationship("Product", back_populates="variants")
    color = relationship("Color", back_populates="variants")
    material = relationship("Material", back_populates="variants")

    supplier_variants = relationship(
        "SupplierVariant",
        back_populates="variant",
        cascade="all, delete-orphan",
    )
    attribute_values = relationship(
        "VariantAttributeValue",
        back_populates="variant",
        cascade="all, delete-orphan",
    )
    variant_usage_roles = relationship(
        "VariantUsageRole",
        back_populates="variant",
        cascade="all, delete-orphan",
    )
    

    # ВАЖНО: БЕЗ cascade — RESTRICT на уровне БД защищает историю
    template_items = relationship("TemplateItem", back_populates="variant")
    quote_items = relationship("QuoteItem", back_populates="variant")

    @property
    def can_be_deleted(self) -> bool:
        """
        Физически удалять можно только если вариант не используется
        в шаблонах и КП.
        """
        return not self.template_items and not self.quote_items

    @property
    def is_available_for_new_quotes(self) -> Column[bool] | bool:
        """
        Можно ли использовать вариант в новых КП/шаблонах.
        """
        return (
            self.status == ProductVariantStatus.ACTIVE
            and self.is_active
            and self.deleted_at is None
        )