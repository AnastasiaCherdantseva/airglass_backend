import uuid
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Material(Base):
    __tablename__ = "materials"
    __table_args__ = (
        Index("ix_material_group_id", "group_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    
    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("material_groups.id", ondelete="RESTRICT"),
        nullable=True,
    )
    
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(
    Boolean,
    default=True,
    nullable=False,
    server_default=text("true"),
)

    # Связи
    group = relationship("MaterialGroup", back_populates="materials")   # ← ДОБАВИТЬ
    variants = relationship("ProductVariant", back_populates="material")