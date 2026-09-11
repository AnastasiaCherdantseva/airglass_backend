import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Integer, Numeric, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

# Конкретные значения специфичных атрибутов для конкретных вариаций товаров
class VariantAttributeValue(Base):
    __tablename__ = "variant_attribute_values"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
    )
    attribute_id = Column(
        UUID(as_uuid=True),
        ForeignKey("attributes.id", ondelete="CASCADE"),
        nullable=False,
    )

    value_string = Column(String(500), nullable=True)
    value_integer = Column(Integer, nullable=True)
    value_decimal = Column(Numeric(14, 4), nullable=True)
    value_boolean = Column(Boolean, nullable=True)
    value_option_id = Column(
        UUID(as_uuid=True),
        ForeignKey("attribute_options.id", ondelete="RESTRICT"),
        nullable=True,
    )

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Связи
    variant = relationship("ProductVariant", back_populates="attribute_values")
    attribute = relationship("Attribute", back_populates="variant_values")
    option = relationship("AttributeOption", back_populates="variant_values")