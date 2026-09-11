import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Numeric, Integer, ForeignKey, Enum, Index, DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class QuoteItemSourceType(str, enum.Enum):
    """Откуда пришла позиция"""
    PRODUCT = "PRODUCT"      # из каталога
    TEMPLATE = "TEMPLATE"    # из шаблона
    MANUAL = "MANUAL"        # добавлена вручную


class QuoteItem(Base):
    """
    Позиция коммерческого предложения.
    
    Хранит snapshot данных на момент добавления.
    Не меняется, даже если товар/цена в каталоге изменились.
    """
    __tablename__ = "quote_items"
    __table_args__ = (
        Index("ix_quote_item_version_id", "quote_version_id"),
        Index("ix_quote_item_group_id", "group_id"),
        Index("ix_quote_item_variant_id", "variant_id"),
        Index("ix_quote_item_product_id", "product_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quote_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quote_item_groups.id", ondelete="CASCADE"),
        nullable=True,
    )

    source_type = Column(
        Enum(QuoteItemSourceType),
        default=QuoteItemSourceType.PRODUCT,
        nullable=False,
    )

    # ========================================
    # ССЫЛКИ НА ИСТОЧНИК (RESTRICT — не удаляются!)
    # ========================================
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=True,
    )
    variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=True,
    )
    supplier_variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("supplier_variants.id", ondelete="RESTRICT"),
        nullable=True,
    )
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("templates.id", ondelete="RESTRICT"),
        nullable=True,
    )
    template_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("template_items.id", ondelete="RESTRICT"),
        nullable=True,
    )

    # ========================================
    # SNAPSHOT (не меняются после сохранения)
    # ========================================
    name_snapshot = Column(Text, nullable=False)
    supplier_name_snapshot = Column(Text, nullable=True)
    supplier_sku_snapshot = Column(Text, nullable=True)
    color_snapshot = Column(Text, nullable=True)
    material_snapshot = Column(Text, nullable=True)

    # ========================================
    # ЦЕНЫ И КОЛИЧЕСТВО
    # ========================================
    quantity = Column(Numeric(14, 4), nullable=False, default=1)
    purchase_price_snapshot = Column(Numeric(14, 2), nullable=False, default=0)
    base_sale_price = Column(Numeric(14, 2), nullable=False, default=0)
    manual_price = Column(Numeric(14, 2), nullable=True)
    discount_percent = Column(Numeric(5, 2), default=0, nullable=False)
    markup_percent = Column(Numeric(5, 2), default=0, nullable=False)
    final_unit_price = Column(Numeric(14, 2), nullable=False, default=0)
    final_total = Column(Numeric(14, 2), nullable=False, default=0)

    sort_order = Column(Integer, default=0, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # ========================================
    # СВЯЗИ
    # ========================================
    quote_version = relationship("QuoteVersion", back_populates="items")
    group = relationship("QuoteItemGroup", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant", back_populates="quote_items")
    supplier_offer = relationship("SupplierVariant", back_populates="quote_items")
    template = relationship("Template", back_populates="quote_items")
    template_item = relationship("TemplateItem", back_populates="quote_items")

    # ========================================
    # СВОЙСТВА
    # ========================================

    @property
    def effective_price(self) -> float:
        """
        Итоговая цена за единицу.
        Приоритет: manual_price > base_sale_price
        """
        if self.manual_price is not None:
            return float(self.manual_price)
        return float(self.base_sale_price)

    @property
    def is_manual_price(self) -> bool:
        """Была ли цена изменена вручную"""
        return self.manual_price is not None

    @property
    def margin(self) -> float:
        """Маржа (прибыль)"""
        return float(self.final_unit_price) - float(self.purchase_price_snapshot)