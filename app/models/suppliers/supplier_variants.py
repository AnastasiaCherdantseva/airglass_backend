import uuid
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin

# Связь поставщика с заказом
class SupplierVariant(Base, TimestampMixin):
    __tablename__ = "supplier_variants"
    __table_args__ = (
        UniqueConstraint("supplier_id", "supplier_sku", name="uq_supplier_sku"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id", ondelete="CASCADE"),
        nullable=False,
    )
    variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    supplier_sku = Column(String(100), nullable=False)
    supplier_name = Column(String(255), nullable=True)
    purchase_price = Column(Numeric(14, 2), nullable=False, default=0, server_default=text("0"))
    minimum_quantity = Column(Numeric(14, 4), nullable=True)
    is_available = Column(Boolean, default=True, nullable=False, server_default=text("true"))
    is_preferred = Column(Boolean, default=False, nullable=False, server_default=text("false"))

    # Связи
    supplier = relationship("Supplier", back_populates="offers")
    variant = relationship("ProductVariant", back_populates="supplier_variants")
    price_history = relationship(
        "SupplierVariantPrice",
        back_populates="supplier_offer",
        cascade="all, delete-orphan",
    )
    quote_items = relationship("QuoteItem", back_populates="supplier_offer")
    template_items = relationship(
        "TemplateItem", back_populates="preferred_supplier_offer"
    )