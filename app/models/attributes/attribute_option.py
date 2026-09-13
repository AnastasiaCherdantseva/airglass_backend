import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

# Варианты атрибутов
class AttributeOption(Base):
    __tablename__ = "attribute_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    attribute_id = Column(
        UUID(as_uuid=True),
        ForeignKey("attributes.id", ondelete="CASCADE"),
        nullable=False,
    )
    value = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False)
    sort_order = Column(
    Integer,
    default=0,
    nullable=False,
    server_default=text("0"),
)
    is_active = Column(
    Boolean,
    default=True,
    nullable=False,
    server_default=text("true"),
)

    # Связи
    attribute = relationship("Attribute", back_populates="options")
    variant_values = relationship("VariantAttributeValue", back_populates="option")