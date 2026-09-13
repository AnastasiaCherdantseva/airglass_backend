import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Color(Base):
    __tablename__ = "colors"
    __table_args__ = (
        Index("ix_color_group_id", "group_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,server_default=text("gen_random_uuid()"))
    
    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("color_groups.id", ondelete="RESTRICT"),
        nullable=True,   
    )
    
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    hex_color = Column(String(7), nullable=True)
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
    group = relationship("ColorGroup", back_populates="colors")   # ← ДОБАВИТЬ
    variants = relationship("ProductVariant", back_populates="color")

    color_visual_types = relationship(
        "ColorVisualType",
        back_populates="color",
        cascade="all, delete-orphan",
        order_by="ColorVisualType.sort_order",
    )

    @property
    def visual_types(self) -> list[str]:
        """Список кодов типов визуализации."""
        return [cvt.visual_type.code for cvt in self.color_visual_types]