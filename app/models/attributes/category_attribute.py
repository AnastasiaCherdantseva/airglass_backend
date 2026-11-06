from sqlalchemy import Column, ForeignKey
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

    # Связи
    category = relationship("Category", back_populates="category_attributes")
    attribute = relationship("Attribute", back_populates="category_attributes")
