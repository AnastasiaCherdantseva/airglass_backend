import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Numeric, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

# Цены у поставщиков на вариации
class SupplierVariantPrice(Base):
    __tablename__ = "supplier_variant_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    supplier_variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("supplier_variants.id", ondelete="CASCADE"),
        nullable=False,
    )
    price = Column(Numeric(14, 2), nullable=False)
    valid_from = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, server_default=text("now()"))
    valid_to = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, server_default=text("now()"))

    # Связи
    supplier_offer = relationship("SupplierVariant", back_populates="price_history")