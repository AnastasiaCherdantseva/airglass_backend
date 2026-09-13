import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class MaterialGroup(Base):
    """
    Группа материалов.

    Примеры:
    - METALS (Металлы)
    - PLASTICS (Пластики)
    - WOOD (Дерево)
    """
    __tablename__ = "material_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
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
    materials = relationship("Material", back_populates="group")
    category_groups = relationship(
        "CategoryMaterialGroup",
        back_populates="material_group",
        cascade="all, delete-orphan",
    )