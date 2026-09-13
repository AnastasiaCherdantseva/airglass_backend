import uuid
from sqlalchemy import Column, ForeignKey, UniqueConstraint, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class CategoryMaterialGroup(Base):
    """
    Какие группы материалов доступны для категории.

    Пример:
    - Ручки          → METALS, PLASTICS, WOOD
    - Стекло         → GLASS
    - Раздвижные     → METALS
    """
    __tablename__ = "category_material_groups"
    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "material_group_id",
            name="uq_category_material_group",
        ),
        Index("ix_category_material_group_category_id", "category_id"),
        Index("ix_category_material_group_group_id", "material_group_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    material_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("material_groups.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Связи
    category = relationship("Category", back_populates="category_material_groups")
    material_group = relationship("MaterialGroup", back_populates="category_groups")