import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.attributes import Attribute
    from app.models.catalog.category import Category


class CategoryAttribute(Base):
    """Link between category and attribute.

    Связь между категорией и атрибутом.
    """

    __tablename__ = "category_attributes"

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    )
    attribute_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attributes.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Связи
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="category_attributes",
    )
    attribute: Mapped["Attribute"] = relationship(
        "Attribute",
        back_populates="category_attributes",
    )
