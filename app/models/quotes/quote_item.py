import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    String, Text, Numeric, Integer, ForeignKey, Enum, Index, DateTime, text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models import (QuoteVersion, QuoteItemGroup, Product,
                                ProductVariant,  SupplierVariant  , Template,
                                       TemplateItem   )

class QuoteItemSourceType(str, enum.Enum):
    """Откуда пришла позиция"""
    PRODUCT = "PRODUCT"
    TEMPLATE = "TEMPLATE"
    MANUAL = "MANUAL"


class QuoteItem(Base):
    """
    Позиция коммерческого предложения.

    Хранит snapshot данных на момент добавления.
    """
    __tablename__ = "quote_items"
    __table_args__ = (
        Index("ix_quote_item_version_id", "quote_version_id"),
        Index("ix_quote_item_group_id", "group_id"),
        Index("ix_quote_item_variant_id", "variant_id"),
        Index("ix_quote_item_product_id", "product_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    quote_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quote_versions.id", ondelete="CASCADE"),
    )
    group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quote_item_groups.id", ondelete="CASCADE"),
    )

    source_type: Mapped[QuoteItemSourceType] = mapped_column(
        Enum(QuoteItemSourceType),
        default=QuoteItemSourceType.PRODUCT,
        server_default=text("'PRODUCT'"),
    )

    # ========================================
    # ССЫЛКИ НА ИСТОЧНИК
    # ========================================
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
    )
    variant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
    )
    supplier_variant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("supplier_variants.id", ondelete="RESTRICT"),
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("templates.id", ondelete="RESTRICT"),
    )
    template_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("template_items.id", ondelete="RESTRICT"),
    )

    # ========================================
    # SNAPSHOT
    # ========================================
    name_snapshot: Mapped[str] = mapped_column(Text)
    supplier_name_snapshot: Mapped[str | None] = mapped_column(Text)
    supplier_sku_snapshot: Mapped[str | None] = mapped_column(Text)
    color_snapshot: Mapped[str | None] = mapped_column(Text)
    material_snapshot: Mapped[str | None] = mapped_column(Text)

    # ========================================
    # ЦЕНЫ И КОЛИЧЕСТВО
    # ========================================
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4),
        default=1,
        server_default=text("1"),
    )
    purchase_price_snapshot: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=0,
        server_default=text("0"),
    )
    base_sale_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=0,
        server_default=text("0"),
    )
    manual_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    discount_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=0,
        server_default=text("0"),
    )
    markup_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=0,
        server_default=text("0"),
    )
    final_unit_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=0,
        server_default=text("0"),
    )
    final_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=0,
        server_default=text("0"),
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
    )
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )

    # ========================================
    # СВЯЗИ
    # ========================================
    quote_version: Mapped["QuoteVersion"] = relationship(back_populates="items")
    group: Mapped["QuoteItemGroup | None"] = relationship(back_populates="items")
    product: Mapped["Product | None"] = relationship()
    variant: Mapped["ProductVariant | None"] = relationship(back_populates="quote_items")
    supplier_offer: Mapped["SupplierVariant | None"] = relationship(back_populates="quote_items")
    template: Mapped["Template | None"] = relationship(back_populates="quote_items")
    template_item: Mapped["TemplateItem | None"] = relationship(back_populates="quote_items")

    # ========================================
    # СВОЙСТВА
    # ========================================

    @property
    def effective_price(self) -> Decimal:
        """
        Итоговая цена за единицу.
        Приоритет: manual_price > base_sale_price
        """
        if self.manual_price is not None:
            return self.manual_price
        return self.base_sale_price

    @property
    def is_manual_price(self) -> bool:
        return self.manual_price is not None

    @property
    def margin(self) -> Decimal:
        """Маржа (прибыль)"""
        return self.final_unit_price - self.purchase_price_snapshot