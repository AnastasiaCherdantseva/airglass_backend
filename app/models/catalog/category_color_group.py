import uuid

from sqlalchemy import Column, ForeignKey, Index, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class CategoryColorGroup(Base):
    """
    Какие группы цветов доступны для категории.

    Пример:
    - Ручки          → FURNITURE
    - Стекло         → RAL
    - Раздвижные     → FURNITURE, STAINLESS
    """

    __tablename__ = "category_color_groups"
    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "color_group_id",
            name="uq_category_color_group",
        ),
        Index("ix_category_color_group_category_id", "category_id"),
        Index("ix_category_color_group_group_id", "color_group_id"),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    color_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("color_groups.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Связи
    category = relationship("Category", back_populates="category_color_groups")
    color_group = relationship("ColorGroup", back_populates="category_groups")
