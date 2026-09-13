import uuid
from sqlalchemy import Column, Numeric, Text, Integer, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class TemplateItem(Base, TimestampMixin):
    __tablename__ = "template_items"
    __table_args__ = (
        Index("ix_template_item_template_id", "template_id"),
        Index("ix_template_item_variant_id", "variant_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    preferred_supplier_variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("supplier_variants.id", ondelete="SET NULL"),
        nullable=True,
    )
    quantity = Column(Numeric(14, 4), nullable=False, default=1,    server_default=text("1"))
    sort_order = Column(
    Integer,
    default=0,
    nullable=False,
    server_default=text("0"),
)
    comment = Column(Text, nullable=True)

    # Связи
    template = relationship("Template", back_populates="items")
    variant = relationship("ProductVariant", back_populates="template_items")
    preferred_supplier_offer = relationship(
        "SupplierVariant", back_populates="template_items"
    )
    quote_items = relationship("QuoteItem", back_populates="template_item")