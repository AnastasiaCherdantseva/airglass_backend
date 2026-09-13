from sqlalchemy import Column, Boolean, Integer, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

# Связь атрибутов с категориями
class CategoryAttribute(Base):
    __tablename__ = "category_attributes"

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    )
    attribute_id = Column(
        UUID(as_uuid=True),
        ForeignKey("attributes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    is_required = Column(Boolean, default=False, nullable=False, server_default=text("false"))
    is_filterable = Column(Boolean, default=False, nullable=False, server_default=text("false"))
    sort_order = Column(
    Integer,
    default=0,
    nullable=False,
    server_default=text("0"),
)

    # Связи
    category = relationship("Category", back_populates="category_attributes")
    attribute = relationship("Attribute", back_populates="category_attributes")